import { useState, type SubmitEvent } from 'react'

function ProfilePanel(): React.JSX.Element {
  const [username, setUsername] = useState('MerlinoErmetico')
  const [bio, setBio] = useState('BruddaOya.')

  function handleSubmit(e: SubmitEvent<HTMLFormElement>): void {
    e.preventDefault()
    console.log('salva profilo', username, bio)
  }

  return (
    <div className="flex-1 bg-bg h-screen flex flex-col items-center justify-center gap-4">
      <div className="relative">
        <div className="w-24 h-24 rounded-full bg-bg-secondary flex items-center justify-center text-3xl text-text">
          M
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