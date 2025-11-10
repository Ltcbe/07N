import React from 'react'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'default' | 'outline' }
export const Button: React.FC<Props> = ({ variant='default', className='', ...props }) => {
  const base = 'input'
  const style = variant === 'outline' ? '' : ' primary'
  return <button {...props} className={base + style + (className ? ' ' + className : '')} />
}
