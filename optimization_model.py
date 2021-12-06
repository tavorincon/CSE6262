from ortools.linear_solver import pywraplp
import pandas as pd
import json

def assign_officers(tot_crimes, num_officers, population, firearms_used, forecast, resolution):
    crimes_by_police = 4

    if resolution == 'month':
        crimes_by_police *= 4

    polices_by_10k_population = 10

    # Join datasets and additional cleanup
    officer_assignments = population.join(forecast.set_index('zip_code'), on='Zip Code').rename(columns={'Zip Code':'zip_code'})
    officer_assignments['Population_Prop'] = officer_assignments['Population'] / officer_assignments['Population'].sum()

    officer_assignments = firearms_used.join(officer_assignments.set_index('zip_code'), on='zip_code')

    officer_assignments = officer_assignments.dropna(subset=['yhat']).reset_index(drop=True)

    officer_assignments['minOfficers'] = round(officer_assignments['Population'] * polices_by_10k_population / 1e4)
    officer_assignments['neededOfficers'] = round(officer_assignments['yhat'] / crimes_by_police)

    # If minOfficers is greater than neededOfficers, then neededOfficers = minOfficers
    officer_assignments.loc[officer_assignments['minOfficers'] > officer_assignments['neededOfficers'], 'neededOfficers'] = officer_assignments['minOfficers']

    officer_assignments['zipCodeRisk'] = officer_assignments['yhat'] * (officer_assignments['FireArmProportion'] + 0.01) / sum(officer_assignments['yhat'])
    num_zipcodes = len(officer_assignments)


    # Chek to see if we have enough officers
    if num_officers < sum(officer_assignments['minOfficers']):
        return """
        ERROR: The number of officers is less than the number of minimum officers.
        Please increase the number of officers or reduce the number of required officers by 10k people.
        """


    # Officer Assignments reset to 0
    officer_assignments['Armed_Officers'] = 0
    officer_assignments['Unarmed_Officers'] = 0

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    ###############################################################################
    # Restrictions
    ###############################################################################

    # Create the variables x for number of police by zipcode
    x = {i: solver.IntVar(0, num_officers, 'x_%i' % i) for i in range(num_zipcodes)}

    # Create the variables y for number of extra police by zipcode
    y = {i: solver.IntVar(0, num_officers, 'y_%i' % i) for i in range(num_zipcodes)}

    # Sum of police must be less than num_officers
    solver.Add(solver.Sum([x[j] for j in range(num_zipcodes)] + [y[j] for j in range(num_zipcodes)]) <= num_officers)

    # Minimum number of polices by zipcode
    for j in range(num_zipcodes):
      solver.Add(x[j] >= officer_assignments['minOfficers'][j])

    # Maximum number of polices by zipcode
    for j in range(num_zipcodes):
      solver.Add(x[j] <= officer_assignments['neededOfficers'][j])

    # Balance assignment of extra police. Assignation of extra police should be +-30% of average extra police per capita by zipcode
    for j in range(num_zipcodes):
      solver.Add(y[j] <= 1.3 * officer_assignments['Population_Prop'][j] * (num_officers - sum(x[i] for i in range(num_zipcodes))))

    ###############################################################################
    # Objective function
    ###############################################################################
    # Objective function. Maximize the sum of risk * number of police by zip code plus the sum of extra police by zip code
    # Crimes with fire arm are more risky that's why we multiply by 100
    objective_terms = [100 * x[i] *  officer_assignments['zipCodeRisk'][i] + (officer_assignments['Population_Prop'][i]) * y[i] for i in range(num_zipcodes)]
    solver.Maximize(solver.Sum(objective_terms))

    ###############################################################################
    # Solution and solve
    ###############################################################################

    # Solve the problem and check if the constraints are satisfied.
    status = solver.Solve()


    # Print solution.
    if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
        # print("Number of police by zipcode:")
        for i in range(num_zipcodes):
            officer_assignments.at[i, 'Armed_Officers'] = int(x[i].solution_value())
    #             print('x_%i = %i' % (i, x[i].solution_value()))

        # print("Number of extra police by zipcode:")
        for i in range(num_zipcodes):
            officer_assignments.at[i, 'Unarmed_Officers'] = int(y[i].solution_value())
    #             print('y_%i = %i' % (i, y[i].solution_value()))
    else:
        return 'The problem does not have an optimal solution.\n'

    print("""Sum of armed officers: {}
    Sum of unarmed officers: {}
    """.format(sum(officer_assignments['Armed_Officers']), sum(officer_assignments['Unarmed_Officers'])))

    # Sort officer_assignments by armed_officers
    officer_assignments.sort_values(by=['Population'], ascending=False)

    return officer_assignments

def generate_geojson(officer_assignations, filtered_by_crime_data, clean_map = False):
  with open('data/map/zipcodes_45mi_clean.geojson') as json_file:
    zip_codes = json.load(json_file)

  # Dictionary of zip codes and count of crimes
  zip_code_crime = {
      str(zipcode): count
      for zipcode, count in zip(officer_assignations['zip_code'], officer_assignations['yhat'])
  }

  # Dictionary of zip codes and count of crimes
  zip_code_armed = {
      str(zipcode): count
      for zipcode, count in zip(officer_assignations['zip_code'], officer_assignations['Armed_Officers'])
  }

  # Dictionary of zip codes and count of crimes
  zip_code_unarmed = {
      str(zipcode): count
      for zipcode, count in zip(officer_assignations['zip_code'], officer_assignations['Unarmed_Officers'])
  }

  # Dictionary of zip codes and count of crimes
  zip_code_filtered = {
      str(zipcode): count
      for zipcode, count in zip(filtered_by_crime_data['zip_code'], filtered_by_crime_data['yhat'])
  }

  # Add count of crimes to geojson
  for feature in zip_codes['features']:
      zipcode = feature['properties']['zipCode']
      feature['properties']['crime_count'] = zip_code_crime.get(zipcode, 0)
      feature['properties']['density'] = zip_code_filtered.get(zipcode, 0)
      feature['properties']['armed_officers'] = zip_code_armed.get(zipcode, 0)
      feature['properties']['unarmed_officers'] = zip_code_unarmed.get(zipcode, 0)

  if clean_map:
    # Remove zip codes with no crimes
    zip_codes['features'] = [
        feature
        for feature in zip_codes['features']
        if feature['properties']['crime_count'] > 0
    ]

  return zip_codes