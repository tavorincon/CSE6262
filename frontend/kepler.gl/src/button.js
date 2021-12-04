import React from 'react';


const buttonStyle = {
  backgroundColor: '#29323C',
  color: '#e2e4e9',
  cursor: 'pointer',
  border: 0,
  borderRadius: '0px',
  fontSize: '15px',
  padding: '8px'
};


const divStyle = {
  position: 'absolute',
  zIndex: 100,
  bottom: 200,
  right: 0,
  backgroundColor: 'white',
  border: 0,
  borderRadius: '5px',
  margin:'30px',
  padding: '12px',
  cursor: 'pointer',
};

const Button = ({onClick, children}) => {
  return(
  <div style={divStyle}>
    <button style={buttonStyle} onClick={() => onClick(-1)}>Prev &#60;&#60;</button>
    <button style={buttonStyle} onClick={() => onClick(0)}>{children}</button>
    <button style={buttonStyle} onClick={() => onClick(1)}>&#62;&#62; Next</button>
</div>
)};

export default Button;
