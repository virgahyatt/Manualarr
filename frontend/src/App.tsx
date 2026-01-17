import { useState } from 'react'
import { Container, Navbar, Row, Col } from 'react-bootstrap'
import ManualUpload from './components/ManualUpload'
import ManualList from './components/ManualList'
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {
  const [refreshKey, setRefreshKey] = useState(0)

  const handleUploadSuccess = () => {
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
          <Col md={4}>
            <h3>Upload Manual</h3>
            <ManualUpload onUploadSuccess={handleUploadSuccess} />
          </Col>
          <Col md={8}>
            <h3>Stored Manuals</h3>
            <ManualList key={refreshKey} />
          </Col>
        </Row>
      </Container>
    </>
  )
}

export default App