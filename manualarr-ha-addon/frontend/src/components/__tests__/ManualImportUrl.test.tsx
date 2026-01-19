import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { Mocked } from 'vitest'
import ManualImportUrl from '../ManualImportUrl'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as Mocked<typeof axios>

describe('ManualImportUrl', () => {
  beforeEach(() => {
    mockedAxios.post.mockReset()
  })

  it('submits url successfully', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({ data: { id: 1 } })
    const onImportSuccess = vi.fn()

    render(<ManualImportUrl onImportSuccess={onImportSuccess} />)

    await user.type(screen.getByLabelText(/Direct PDF Link/i), 'http://example.com/test.pdf')
    await user.click(screen.getByRole('button', { name: /Import/i }))

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/manuals/import', {
        url: 'http://example.com/test.pdf',
        brand: null,
        model: null
      })
      expect(onImportSuccess).toHaveBeenCalled()
      expect(screen.getByText(/Manual imported successfully/i)).toBeInTheDocument()
    })
  })
})
