import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import type { Mocked } from 'vitest'
import ManualUpload from '../ManualUpload'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as Mocked<typeof axios>

describe('ManualUpload', () => {
  it('submits the form successfully', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({ data: { id: 1 } })
    const onUploadSuccess = vi.fn()

    const { container } = render(<ManualUpload onUploadSuccess={onUploadSuccess} />)

    await user.type(screen.getByLabelText(/Brand/i), 'Sony')
    await user.type(screen.getByLabelText(/Model/i), 'TV')
    
    const file = new File(['hello'], 'manual.pdf', { type: 'application/pdf' })
    const input = screen.getByLabelText(/Select Manual/i) as HTMLInputElement
    await user.upload(input, file)

    // Bypass browser validation in jsdom by triggering submit directly
    const form = container.querySelector('form')
    if (form) fireEvent.submit(form)

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalled()
      expect(onUploadSuccess).toHaveBeenCalled()
    })
  })
})
