/** LA City brand tokens — sourced from styleguide.lacity.gov */

export const colors = {
  primaryNavy: '#1c2253',
  deepNavy: '#161f50',
  background: '#ffffff',
  bodyText: '#333333',
  success: '#089e00',
  error: '#ff0000',
  warning: '#fff664',
  info: '#000db5',
  lightGray: '#f5f5f5',
  borderGray: '#d9d9d9',
  white: '#ffffff',
} as const;

export const fonts = {
  primary: "'Open Sans', sans-serif",
  heading: "'Montserrat', sans-serif",
  accent: "'Lato', sans-serif",
} as const;

export const typography = {
  h1: { size: '40px', weight: 600 },
  h2: { size: '32px', weight: 600 },
  h3: { size: '28px', weight: 600 },
  h4: { size: '24px', weight: 600 },
  h5: { size: '20px', weight: 600 },
  body: { size: '16px', weight: 400, lineHeight: '24px' },
} as const;
