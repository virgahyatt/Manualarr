import { useState } from 'react'
import { Container, Navbar, Row, Col, Tabs, Tab } from 'react-bootstrap'
import ManualUpload from './components/ManualUpload'
import ManualList from './components/ManualList'
import ManualSearch from './components/ManualSearch'
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {
  const [refreshKey, setRefreshKey] = useState(0)

  const handleSuccess = () => {
    setRefreshKey(prev => prev + 1)
  }

  return (
    <>
      <Navbar bg="dark" variant="dark" className="mb-4">
        <Container>
          <Navbar.Brand href="#home">Manualarr</Navbar.Brand>
        </Container>
      </Navbar>

      <Container>
        <Row>
          <Col md={5}>
            <h3>Add Manual</h3>
            <Tabs defaultActiveKey="upload" id="add-manual-tabs" className="mb-3">
              <Tab eventKey="upload" title="Upload">
                <ManualUpload onUploadSuccess={handleSuccess} />
              </Tab>
              <Tab eventKey="search" title="Search Online">
                <ManualSearch onImportSuccess={handleSuccess} />
              </Tab>
            </Tabs>
          </Col>
          <Col md={7}>
            <h3>Stored Manuals</h3>
            <ManualList key={refreshKey} />
          </Col>
        </Row>
      </Container>
    </>
  )
}

export default App
