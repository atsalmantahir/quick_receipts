import React from 'react';
import { CContainer, CRow, CCol, CCard, CCardBody, CCardHeader } from '@coreui/react';
import '@coreui/coreui/dist/css/coreui.min.css'; // Import Core UI styles

function App() {
  return (
    <div className="App">
      <CContainer>
        <CRow>
          <CCol xs="12" sm="6" md="4">
            <CCard>
              <CCardHeader>
                Core UI Card
              </CCardHeader>
              <CCardBody>
                <p>This is a Core UI component integrated into React.</p>
              </CCardBody>
            </CCard>
          </CCol>
        </CRow>
      </CContainer>
    </div>
  );
}

export default App;
