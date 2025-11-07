import React from 'react';
import PropTypes from 'prop-types';

const variants = {
  primary: {
    background: 'linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(37,99,235,0.1) 100%)',
    borderColor: 'rgba(37, 99, 235, 0.35)',
  },
  success: {
    background: 'linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(5,150,105,0.1) 100%)',
    borderColor: 'rgba(16, 185, 129, 0.35)',
  },
  danger: {
    background: 'linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(220,38,38,0.1) 100%)',
    borderColor: 'rgba(239, 68, 68, 0.35)',
  },
};

function DashboardCard({ title, value, subtitle, variant }) {
  const styles = variants[variant] || variants.primary;
  return (
    <div className="card" style={styles}>
      <span className="card__title">{title}</span>
      <span className="card__value">{value}</span>
      <span className="card__subtitle">{subtitle}</span>
    </div>
  );
}

DashboardCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  subtitle: PropTypes.string,
  variant: PropTypes.oneOf(['primary', 'success', 'danger']),
};

DashboardCard.defaultProps = {
  subtitle: '',
  variant: 'primary',
};

export default DashboardCard;
