import { useState, useEffect } from "react"

/*Conversation preview elements: name and last message.
When clicked, it will call the onSelectConversation function with the conversation's id as an argument.
The onNewConversation function is called when the "+" button is clicked, allowing the user to start a new conversation.
*/
interface Conversation {
  id: number
  type: string
  name: string | null
  display_name: string | null
  other_user_id: number | null
  created_at: string
  created_by: number
}

interface ContextMenuState {
  conversationId: number
  conversationType: string
  x: number
  y: number
}

interface SidebarProps {
  onSelectConversation: (conversation: Conversation) => void
  onNewConversation: () => void
  onViewProfile: (userId: number) => void
  onConversationCleared: (conversationId: number) => void
  onConversationDeleted: (conversationId: number) => void
  accessToken: string | null
  refreshKey: number
}

function Sidebar({
  onSelectConversation,
  onNewConversation,
  onViewProfile,
  onConversationCleared,
  onConversationDeleted,
  accessToken,
  refreshKey
}: SidebarProps): React.JSX.Element{

    const [conversations, setConversations] = useState<Conversation[]>([])
    const [searchQuery, setSearchQuery] = useState('')
    const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null)

    useEffect(() => {
      async function loadConversations(): Promise<void> {
        const response = await fetch('http://127.0.0.1:8000/conversations', {
          headers: { Authorization: `Bearer ${accessToken}` }
        })

        if (!response.ok) {
          console.log('errore caricamento conversazioni', response.status)
          return
        }

        const data = await response.json()
        setConversations(data)
      }

      loadConversations()
    }, [refreshKey])

    const filteredConversations = conversations.filter((conversation) =>
        (conversation.display_name ?? '').toLowerCase().includes(searchQuery.toLowerCase())
    )

    function handleBlock(): void {
      //Placeholder: "Blocca" behaviour is still to be designed, per project backlog.
      console.log('blocca utente — non ancora implementato')
      setContextMenu(null)
    }

    async function handleClear(conversationId: number): Promise<void> {
      const response = await fetch(`http://127.0.0.1:8000/conversations/${conversationId}/messages`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` }
      })

      setContextMenu(null)

      if (!response.ok) {
        console.log('errore svuotamento conversazione', response.status)
        return
      }

      onConversationCleared(conversationId)
    }

    async function handleDelete(conversationId: number): Promise<void> {
      const response = await fetch(`http://127.0.0.1:8000/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` }
      })

      setContextMenu(null)

      if (!response.ok) {
        console.log('errore cancellazione conversazione', response.status)
        return
      }

      setConversations(conversations.filter((conversation) => conversation.id !== conversationId))
      onConversationDeleted(conversationId)
    }

    async function handleLeaveGroup(conversationId: number): Promise<void> {
      const response = await fetch(`http://127.0.0.1:8000/conversations/${conversationId}/leave`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` }
      })

      setContextMenu(null)

      if (!response.ok) {
        console.log('errore uscita dal gruppo', response.status)
        return
      }

      setConversations(conversations.filter((conversation) => conversation.id !== conversationId))
      onConversationDeleted(conversationId)
    }

    return (
    <div className="w-72 bg-bg-secondary h-screen flex flex-col relative">
      <div className="flex items-center justify-between px-4 py-3">
        <p className="text-text font-semibold">Chat</p>
        <button
          onClick={onNewConversation}
          className="w-8 h-8 rounded-full bg-accent hover:bg-accent-hover text-text flex items-center justify-center text-lg"
        >
          +
        </button>
      </div>

      <div className="px-4 pb-3">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Cerca chat"
          className="w-full bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none text-sm"
        />
      </div>

      <div className="flex-1 overflow-y-auto">
        {filteredConversations.map((conversation) => (
          <div
            key={conversation.id}
            onClick={() => onSelectConversation(conversation)}
            onContextMenu={(e) => {
              e.preventDefault()
              setContextMenu({
                conversationId: conversation.id,
                conversationType: conversation.type,
                x: e.clientX,
                y: e.clientY
              })
            }}
            className="flex items-center gap-3 px-4 py-3 hover:bg-bg-tertiary cursor-pointer"
          >
            <div
              onClick={(e) => {
                e.stopPropagation()
                if (conversation.other_user_id !== null) {
                  onViewProfile(conversation.other_user_id)
                }
              }}
              className="w-10 h-10 shrink-0 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold"
            >
              {(conversation.display_name ?? 'C').charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-text font-semibold truncate">{conversation.display_name}</p>
            </div>
          </div>
        ))}
      </div>

      {contextMenu && (
        <>
          <div onClick={() => setContextMenu(null)} className="fixed inset-0 z-10"></div>
          <div
            style={{ position: 'fixed', top: contextMenu.y, left: contextMenu.x }}
            className="z-20 bg-bg-tertiary rounded shadow flex flex-col overflow-hidden w-44"
          >
            {contextMenu.conversationType === 'group' ? (
              <>
                <button
                  onClick={() => handleClear(contextMenu.conversationId)}
                  className="text-left px-3 py-2 text-sm text-text hover:bg-accent"
                >
                  Svuota conversazione
                </button>
                <button
                  onClick={() => handleLeaveGroup(contextMenu.conversationId)}
                  className="text-left px-3 py-2 text-sm text-red-400 hover:bg-accent"
                >
                  Lascia gruppo
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleBlock}
                  className="text-left px-3 py-2 text-sm text-text hover:bg-accent"
                >
                  Blocca
                </button>
                <button
                  onClick={() => handleClear(contextMenu.conversationId)}
                  className="text-left px-3 py-2 text-sm text-text hover:bg-accent"
                >
                  Svuota conversazione
                </button>
                <button
                  onClick={() => handleDelete(contextMenu.conversationId)}
                  className="text-left px-3 py-2 text-sm text-red-400 hover:bg-accent"
                >
                  Cancella conversazione
                </button>
              </>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default Sidebar
