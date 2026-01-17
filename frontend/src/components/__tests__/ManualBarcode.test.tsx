import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ManualBarcode from '../ManualBarcode'

// Mock html5-qrcode
vi.mock('html5-qrcode', () => {
  return {
    Html5QrcodeScanner: class {
      render() {}
      clear() { return Promise.resolve(true) }
      pause() {}
      resume() {}
    }
  }
})

vi.mock('axios')

describe('ManualBarcode', () => {
  it('renders scanner', () => {
    const onProductFound = vi.fn()
    render(<ManualBarcode onProductFound={onProductFound} />)
    expect(screen.getByText(/Point your camera/i)).toBeInTheDocument()
  })
})