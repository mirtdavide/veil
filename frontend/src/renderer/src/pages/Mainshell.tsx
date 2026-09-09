import { useState } from 'react'
import IconRail from '../components/IconRail'
import Sidebar from '../components/Sidebar'
import ChatPanel from './ChatPanel'
import ProfilePanel from './ProfilePanel'
import SearchPanel from './SearchPanel'
import NewChatPanel from './NewChatPanel'
import PendingRequestsPanel from './PendingRequestsPanel'

type RightPanelMode = 'chat' | 'profile' | 'search' | 'newChat' | 'pendingRequests'

function MainShell(): React.JSX.Element {
  const [rightPanelMode, setRightPanelMode] = useState<RightPanelMode>('chat')

  function handleOpenProfile(): void {
    setRightPanelMode('profile')
  }

  function handleOpenSearch(): void {
    setRightPanelMode('search')
  }

  function handleOpenPendingRequests(): void {
    setRightPanelMode('pendingRequests')
  }

  function handleSelectConversation(conversationId: number): void {
    console.log('conversazione selezionata', conversationId)
    setRightPanelMode('chat')
  }

  function handleNewConversation(): void {
    setRightPanelMode('newChat')
  }

  function handleSendRequest(userId: number): void {
    console.log('richiesta inviata', userId)
  }

  function handleStartChat(userId: number): void {
    console.log('avvia chat con', userId)
    setRightPanelMode('chat')
  }

  function handleAcceptRequest(requestId: number): void {
    console.log('accettata richiesta', requestId)
  }

  function handleRefuseRequest(requestId: number): void {
    console.log('rifiutata richiesta', requestId)
  }

  return (
    <div className="flex">
      <IconRail
        onOpenProfile={handleOpenProfile}
        onOpenSearch={handleOpenSearch}
        onOpenPendingRequests={handleOpenPendingRequests}
      />
      <Sidebar onSelectConversation={handleSelectConversation} onNewConversation={handleNewConversation} />
      {rightPanelMode === 'chat' && <ChatPanel />}
      {rightPanelMode === 'profile' && <ProfilePanel />}
      {rightPanelMode === 'search' && <SearchPanel onSendRequest={handleSendRequest} />}
      {rightPanelMode === 'newChat' && <NewChatPanel onStartChat={handleStartChat} />}
      {rightPanelMode === 'pendingRequests' && (
        <PendingRequestsPanel onAcceptRequest={handleAcceptRequest} onRefuseRequest={handleRefuseRequest} />
      )}
    </div>
  )
}

export default MainShell