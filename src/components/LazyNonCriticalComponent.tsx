import React from 'react';

const LazyNonCriticalComponent: React.FC = () => {
  return (
    <>
      {/* Non-critical, heavy, or rarely used UI here */}
      <p>Lazy loaded non-critical component.</p>
    </>
  );
};

export default LazyNonCriticalComponent; 