import React from 'react';
import { CSpinner } from '@coreui/react';

const Loader = () => {
  return (
    <div className="loader">
      <CSpinner color="primary" />
    </div>
  );
};

export default Loader;