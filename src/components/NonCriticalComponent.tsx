import React from 'react';

const NonCriticalComponent: React.FC = () => {
  return (
    <>
      {/* Non-critical content here */}
    </>
  );
};

export default React.memo(NonCriticalComponent); 