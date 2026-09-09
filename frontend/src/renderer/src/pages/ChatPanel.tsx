import { useState, type SubmitEvent } from 'react'

interface Message {
  id: number
  text: string
  fromMe: boolean
}

const messages: Message[] = [
  { id: 1, text: 'Oya', fromMe: false },
  { id: 2, text: 'Brudda', fromMe: true },
  { id: 3, text: 'Crazy', fromMe: false }
]

function ChatPanel(): React.JSX.Element {
  const [draft, setDraft] = useState('')

  function handleSend(e: SubmitEvent<HTMLFormElement>): void {
    e.preventDefault()
    if (draft.trim() === '') return
    console.log('invia messaggio', draft)
    setDraft('')
  }

  return (
    <div className="flex-1 bg-bg h-screen flex flex-col">
      <div className="flex items-center gap-3 px-4 py-3 bg-bg-secondary">
        <div className="w-10 h-10 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold">
          I
        </div>
        <p className="text-text font-semibold">ilpelato</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
        {messages.map((message) => (
          <div
            key={message.id}
            className={
              message.fromMe
                ? 'self-end bg-accent text-text px-3 py-2 rounded max-w-xs'
                : 'self-start bg-bg-secondary text-text px-3 py-2 rounded max-w-xs'
            }
          >
            {message.text}
          </div>
        ))}
      </div>

      <form onSubmit={handleSend} className="flex gap-2 p-4">
        <button
          type="button"
          aria-label="Allega file"
          className="w-10 h-10 shrink-0 rounded-full bg-bg-tertiary hover:bg-bg-secondary flex items-center justify-center text-text"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
          </svg>
        </button>
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Scrivi un messaggio"
          className="flex-1 bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
        />
        <button
          type="submit"
          className="bg-accent hover:bg-accent-hover text-text rounded px-4 py-2 font-semibold"
        >
          Invia
        </button>
      </form>
    </div>
  )
}

export default ChatPanel