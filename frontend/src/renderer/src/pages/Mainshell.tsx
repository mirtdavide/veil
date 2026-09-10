import { useState } from 'react'
import IconRail from '../components/IconRail'
import Sidebar from '../components/Sidebar'
import ChatPanel from './ChatPanel'
import ProfilePanel from './ProfilePanel'
import SearchPanel from './SearchPanel'
import NewChatPanel from './NewChatPanel'
import PendingRequestsPanel from './PendingRequestsPanel'
interface CurrentUser {
  id: number
  username: string
  email: string
}

interface MainShellProps {
  accessToken: string | null
}
type RightPanelMode = 'chat' | 'profile' | 'search' | 'newChat' | 'pendingRequests'

function MainShell({ accessToken, currentUser  }: MainShellProps): React.JSX.Element {
  const [rightPanelMode, setRightPanelMode] = useState<RightPanelMode>('chat')
  const [selectedConversationId, setSelectedConversationId] = useState<number | null>(null)
  function handleOpenProfile(): void {
    setRightPanelMode('profile')
  }

  function handleCreateGroup(userIds: number[]): void {
    console.log('crea gruppo con', userIds)
    setRightPanelMode('chat')
  }

  function handleOpenSearch(): void {
    setRightPanelMode('search')
  }

  function handleOpenPendingRequests(): void {
    setRightPanelMode('pendingRequests')
  }

  function handleSelectConversation(conversationId: number): void {
    setSelectedConversationId(conversationId)
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
      <Sidebar onSelectConversation={handleSelectConversation} onNewConversation={handleNewConversation} accessToken={accessToken}/>
      {rightPanelMode === 'chat' && selectedConversationId !== null && (
        <ChatPanel
          conversationId={selectedConversationId}
          accessToken={accessToken}
          currentUserId={currentUser?.id ?? 0}
        />
      )}
      {rightPanelMode === 'profile' && <ProfilePanel accessToken={accessToken} />}
      {rightPanelMode === 'search' && <SearchPanel onSendRequest={handleSendRequest} />}
      {rightPanelMode === 'newChat' && <NewChatPanel onStartChat={handleStartChat} onCreateGroup={handleCreateGroup} />}
      {rightPanelMode === 'pendingRequests' && (
        <PendingRequestsPanel onAcceptRequest={handleAcceptRequest} onRefuseRequest={handleRefuseRequest} />
      )}
    </div>
  )
}

export default MainShell