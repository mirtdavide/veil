import {useState} from "react"

/*Conversation preview elements: name and last message. 
When clicked, it will call the onSelectConversation function with the conversation's id as an argument. 
The onNewConversation function is called when the "+" button is clicked, allowing the user to start a new conversation.
*/
interface Conversation {
    id: number
    name: string
    lastMessage: string
}

interface SidebarProps {
    onSelectConversation: (conversationId: number) => void
    onNewConversation: () => void
}

const conversations: Conversation[] = [
        { id: 1, name: 'Clown', lastMessage: 'oya brudda?' },
        { id: 2, name: 'Libertà di parola', lastMessage: 'Ivin: zio pera' },
        { id: 3, name: 'Luchino', lastMessage: 'Foto Pipo' }
        ]

function Sidebar({onSelectConversation, onNewConversation}: SidebarProps): React.JSX.Element {

    const [searchQuery, setSearchQuery] = useState('')
    const filteredConversations = conversations.filter((conversation) =>
        conversation.name.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
    <div className="w-72 bg-bg-secondary h-screen flex flex-col">
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
            onClick={() => onSelectConversation(conversation.id)}
            className="flex items-center gap-3 px-4 py-3 hover:bg-bg-tertiary cursor-pointer"
          >
            <div className="w-10 h-10 shrink-0 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold">
              {conversation.name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-text font-semibold truncate">{conversation.name}</p>
              <p className="text-text-muted text-sm truncate">{conversation.lastMessage}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Sidebar