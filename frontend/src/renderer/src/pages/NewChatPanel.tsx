import { useState } from 'react'
import { useEffect } from 'react'

interface Friend {
  id: number
  username: string
}

interface NewChatPanelProps {
  accessToken: string | null
  onStartChat: (userId: number) => void
  onCreateGroup: (userIds: number[], groupName: string) => void
  onViewProfile: (userId: number) => void
}






function NewChatPanel({ accessToken, onStartChat, onCreateGroup, onViewProfile }: NewChatPanelProps): React.JSX.Element {
  const [isGroupMode, setIsGroupMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [friends, setFriends] = useState<Friend[]>([])
  const [groupName, setGroupName] = useState('')

  useEffect(() => {

    async function loadFriends(): Promise <void>{

      const response = await fetch('http://127.0.0.1:8000/connections', {
            headers: { Authorization: `Bearer ${accessToken}` }
      })

      if(!response.ok){
        console.log('Error while loading friends list', response.status)
        return
      }

      const data = await response.json()
      setFriends(data)




    }
    loadFriends()

  }, [])
  
  function handleToggleGroupMode(): void {
  setIsGroupMode(!isGroupMode)
  setSelectedIds([])
}
  function handleFriendClick(friendId: number): void {
    if (!isGroupMode) {
      onStartChat(friendId)
      return
    }

    if (selectedIds.includes(friendId)) {
      setSelectedIds(selectedIds.filter((id) => id !== friendId))
    } else {
      setSelectedIds([...selectedIds, friendId])
    }
  }

  return (
    <div className="flex-1 bg-bg h-screen flex flex-col p-4 gap-2">
      <button
        onClick={handleToggleGroupMode}
        className="bg-bg-tertiary hover:bg-accent text-text rounded py-2 text-sm font-semibold"
      >
        {isGroupMode ? 'Annulla gruppo' : 'Crea gruppo'}
      </button>

      {friends.map((friend) => (
        <div
          key={friend.id}
          onClick={() => handleFriendClick(friend.id)}
          className={
            selectedIds.includes(friend.id)
            ? 'flex items-center gap-3 px-3 py-2 bg-accent cursor-pointer rounded'
            : 'flex items-center gap-3 px-3 py-2 bg-bg-secondary hover:bg-bg-tertiary cursor-pointer rounded'
            }
        >
          <div
            onClick={(e) => {
              e.stopPropagation()
              onViewProfile(friend.id)
            }}
            className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold text-sm"
          >
            {friend.username.charAt(0).toUpperCase()}
          </div>
          <p className="text-text">{friend.username}</p>
        </div>
      ))}
      {isGroupMode && (
      <input
        type="text"
        value={groupName}
        onChange={(e) => setGroupName(e.target.value)}
        placeholder="Nome del gruppo"
        className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
      />
      )}

      {isGroupMode && selectedIds.length >= 2 && (
      
        <button
          onClick={() => onCreateGroup(selectedIds, groupName)}
          className="bg-accent hover:bg-accent-hover text-text rounded py-2 text-sm font-semibold"
        >
          Crea gruppo ({selectedIds.length})
        </button>
      )}
    </div>
  )
}

export default NewChatPanel