import { useState, useEffect, type SubmitEvent } from 'react'

interface ProfilePanelProps {
  accessToken: string | null
}

function ProfilePanel({ accessToken }: ProfilePanelProps): React.JSX.Element {
  const [username, setUsername] = useState('')
  const [bio, setBio] = useState('')

  useEffect(() => {
    async function loadProfile(): Promise<void> {
      const response = await fetch('http://127.0.0.1:8000/auth/me', {
        headers: { Authorization: `Bearer ${accessToken}` }
      })

      if (!response.ok) {
        console.log('errore caricamento profilo', response.status)
        return
      }

      const data = await response.json()
      setUsername(data.username)
      setBio(data.bio ?? '')
    }

    loadProfile()
  }, [])

  async function handleSubmit(e: SubmitEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()

    const response = await fetch('http://127.0.0.1:8000/auth/me', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`
      },
      body: JSON.stringify({ username, bio })
    })

    if (!response.ok) {
      console.log('errore salvataggio profilo', response.status)
      return
    }

    console.log('profilo salvato')
  }

  return (
    <div className="flex-1 bg-bg h-screen flex flex-col items-center justify-center gap-4">
      <div className="relative">
        <div className="w-24 h-24 rounded-full bg-bg-secondary flex items-center justify-center text-3xl text-text">
          {(username || 'U').charAt(0).toUpperCase()}
        </div>
        <div className="absolute bottom-0 right-0 w-7 h-7 rounded-full bg-accent border-2 border-bg"></div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col items-center gap-4">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="bg-bg-tertiary text-text rounded px-3 py-2 outline-none text-center w-56"
        />
        <textarea
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          rows={3}
          className="bg-bg-tertiary text-text rounded px-3 py-2 outline-none w-56 resize-none"
        />
        <button
          type="submit"
          className="bg-accent hover:bg-accent-hover text-text rounded py-2 w-56 font-semibold"
        >
          Salva modifiche
        </button>
      </form>
    </div>
  )
}

export default ProfilePanel