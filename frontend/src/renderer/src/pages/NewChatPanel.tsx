import { useState } from 'react'

interface Friend {
  id: number
  username: string
}

const friends: Friend[] = [
  { id: 1, username: 'ilpelato' },
  { id: 2, username: 'gheia' },
  { id: 3, username: 'omgitsandre' }
]

interface NewChatPanelProps {
  onStartChat: (userId: number) => void
}

function NewChatPanel({ onStartChat }: NewChatPanelProps): React.JSX.Element {
  const [isGroupMode, setIsGroupMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<number[]>([])

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
        onClick={() => setIsGroupMode(!isGroupMode)}
        className="bg-bg-tertiary hover:bg-accent text-text rounded py-2 text-sm font-semibold"
      >
        {isGroupMode ? 'Annulla gruppo' : 'Crea gruppo'}
      </button>

      {friends.map((friend) => (
        <div
          key={friend.id}
          onClick={() => handleFriendClick(friend.id)}
          className="flex items-center gap-3 px-3 py-2 bg-bg-secondary hover:bg-bg-tertiary cursor-pointer rounded"
        >
          <div className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold text-sm">
            {friend.username.charAt(0).toUpperCase()}
          </div>
          <p className="text-text">{friend.username}</p>
        </div>
      ))}
    </div>
  )
}

export default NewChatPanel