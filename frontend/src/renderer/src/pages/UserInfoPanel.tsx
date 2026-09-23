import { useState, useEffect } from 'react'

interface UserProfile {
  id: number
  username: string
  bio: string | null
  avatar_path: string | null
}

interface UserInfoPanelProps {
  userId: number
  accessToken: string | null
}

function UserInfoPanel({ userId, accessToken }: UserInfoPanelProps): React.JSX.Element {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isAvatarExpanded, setIsAvatarExpanded] = useState(false)

  useEffect(() => {
    async function loadProfile(): Promise<void> {
      const response = await fetch(`http://127.0.0.1:8000/users/${userId}`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      })

      if (!response.ok) {
        console.log('errore caricamento profilo utente', response.status)
        return
      }

      const data = await response.json()
      setProfile(data)
    }

    setIsAvatarExpanded(false)
    loadProfile()
  }, [userId])

  return (
    <div className="flex-1 bg-bg h-screen flex flex-col items-center justify-center gap-4">
      <div
        onClick={() => profile?.avatar_path && setIsAvatarExpanded(true)}
        className={
          profile?.avatar_path
            ? 'w-24 h-24 rounded-full bg-bg-secondary flex items-center justify-center text-3xl text-text cursor-pointer overflow-hidden'
            : 'w-24 h-24 rounded-full bg-bg-secondary flex items-center justify-center text-3xl text-text'
        }
      >
        {profile?.avatar_path ? (
          <img
            src={profile.avatar_path}
            alt={profile.username}
            className="w-full h-full object-cover"
          />
        ) : (
          (profile?.username ?? '?').charAt(0).toUpperCase()
        )}
      </div>
      <p className="text-text text-xl font-semibold">{profile?.username ?? '...'}</p>
      <p className="text-text-muted text-sm text-center max-w-xs">
        {profile?.bio ?? 'Nessuna bio'}
      </p>

      {isAvatarExpanded && profile?.avatar_path && (
        <div
          onClick={() => setIsAvatarExpanded(false)}
          className="fixed inset-0 bg-black/80 flex items-center justify-center cursor-pointer"
        >
          <img
            src={profile.avatar_path}
            alt={profile.username}
            className="max-w-md max-h-md rounded-lg"
          />
        </div>
      )}
    </div>
  )
}

export default UserInfoPanel
