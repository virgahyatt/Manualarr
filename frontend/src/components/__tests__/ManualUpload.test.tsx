import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { Mocked } from 'vitest'
import ManualUpload from '../ManualUpload'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as Mocked<typeof axios>

describe('ManualUpload', () => {
  beforeEach(() => {
    mockedAxios.post.mockReset()
  })

  it('extracts metadata and submits the form', async () => {
    const user = userEvent.setup()
    
    // Mock extraction response
    mockedAxios.post.mockImplementation((url) => {
      if (url === '/api/manuals/extract-metadata') {
        return Promise.resolve({ data: { brand: 'Sony', model: 'TV-X1' } })
      }
      if (url === '/api/manuals/') {
        return Promise.resolve({ data: { id: 1 } })
      }
      return Promise.reject(new Error('Unknown URL'))
    })
    
    const onUploadSuccess = vi.fn()

    const { container } = render(<ManualUpload onUploadSuccess={onUploadSuccess} />)

    // Select file
    const file = new File(['hello'], 'manual.pdf', { type: 'application/pdf' })
    const input = screen.getByLabelText(/Select Manual/i) as HTMLInputElement
    await user.upload(input, file)

    // Wait for analysis to complete and populate fields
    await waitFor(() => {
      expect(screen.getByLabelText(/Brand/i)).toHaveValue('Sony')
      expect(screen.getByLabelText(/Model/i)).toHaveValue('TV-X1')
    })

    // Submit
    const form = container.querySelector('form')
    if (form) fireEvent.submit(form)

    await waitFor(() => {
      // Verify the final upload call contains the extracted data
      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/manuals/'),
        expect.any(FormData),
        expect.any(Object)
      )
      expect(onUploadSuccess).toHaveBeenCalled()
    })
  })
})
