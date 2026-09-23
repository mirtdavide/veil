import { useState } from 'react'
import IconRail from '../components/IconRail'
import Sidebar from '../components/Sidebar'
import ChatPanel from './ChatPanel'
import ProfilePanel from './ProfilePanel'
import SearchPanel from './SearchPanel'
import NewChatPanel from './NewChatPanel'
import PendingRequestsPanel from './PendingRequestsPanel'
import UserInfoPanel from './UserInfoPanel'
interface CurrentUser {
  id: number
  username: string
  email: string
}

interface Conversation {
  id: number
  type: string
  name: string | null
  display_name: string | null
  other_user_id: number | null
  created_at: string
  created_by: number
}

interface MainShellProps {
  accessToken: string | null
  currentUser: CurrentUser | null
}
type RightPanelMode = 'chat' | 'profile' | 'search' | 'newChat' | 'pendingRequests' | 'userInfo'

function MainShell({ accessToken, currentUser  }: MainShellProps): React.JSX.Element {
  const [rightPanelMode, setRightPanelMode] = useState<RightPanelMode>('chat')
  const [selectedConversationId, setSelectedConversationId] = useState<number | null>(null)
  const [selectedConversationName, setSelectedConversationName] = useState('')
  const [selectedConversationOtherUserId, setSelectedConversationOtherUserId] = useState<number | null>(null)
  const [selectedProfileUserId, setSelectedProfileUserId] = useState<number | null>(null)
  const [conversationRefreshKey, setConversationRefreshKey] = useState(0)
  const [messagesRefreshKey, setMessagesRefreshKey] = useState(0)
  function handleOpenProfile(): void {
    setRightPanelMode('profile')
  }

  //A conversation's messages were wiped from another part of the UI (the sidebar's
  //context menu). If that's the conversation currently open, force ChatPanel to reload.
  function handleConversationCleared(conversationId: number): void {
    if (conversationId === selectedConversationId) {
      setMessagesRefreshKey((previous) => previous + 1)
    }
  }

  //A conversation was deleted entirely. If it was the one open, close it.
  function handleConversationDeleted(conversationId: number): void {
    if (conversationId === selectedConversationId) {
      setSelectedConversationId(null)
    }
  }

  function handleViewProfile(userId: number): void {
    setSelectedProfileUserId(userId)
    setRightPanelMode('userInfo')
  }

  //Opens a conversation that was just created or reopened via POST /conversations,
  //which now always includes display_name/other_user_id computed by the backend.
  function openConversation(conversation: Conversation): void {
    setSelectedConversationId(conversation.id)
    setSelectedConversationName(conversation.display_name ?? 'Conversazione')
    setSelectedConversationOtherUserId(conversation.other_user_id)
    setRightPanelMode('chat')
  }

  async function handleCreateGroup(userIds: number[], groupName: string): Promise<void> {
    const response = await fetch('http://127.0.0.1:8000/conversations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`
      },
      body: JSON.stringify({ type: 'group', name: groupName, member_ids: userIds })
    })

    if (!response.ok) {
      console.log('errore creazione gruppo', response.status)
      return
    }

    const conversation = await response.json()
    openConversation(conversation)
    setConversationRefreshKey((previous) => previous + 1)
  }

  function handleOpenSearch(): void {
    setRightPanelMode('search')
  }

  function handleOpenPendingRequests(): void {
    setRightPanelMode('pendingRequests')
  }

  function handleSelectConversation(conversation: Conversation): void {
    openConversation(conversation)
  }

  function handleNewConversation(): void {
    setRightPanelMode('newChat')
  }

  async function handleStartChat(userId: number): Promise<void> {

    const response = await fetch('http://127.0.0.1:8000/conversations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`
      },
      body: JSON.stringify({ type: 'direct', name: null, member_ids: [userId] })
    })

    if(!response.ok){

      console.log('Error while loading chat', response.status)
      return
    }

    const conversation = await response.json()
    openConversation(conversation)
    setConversationRefreshKey((previous)=> previous + 1)

  }


  return (
    <div className="flex">
      <IconRail

        onOpenProfile={handleOpenProfile}
        onOpenSearch={handleOpenSearch}
        onOpenPendingRequests={handleOpenPendingRequests}
      />
      <Sidebar
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onViewProfile={handleViewProfile}
        onConversationCleared={handleConversationCleared}
        onConversationDeleted={handleConversationDeleted}
        accessToken={accessToken}
        refreshKey={conversationRefreshKey}
      />
      {rightPanelMode === 'chat' && selectedConversationId !== null && (
        <ChatPanel
          conversationId={selectedConversationId}
          conversationName={selectedConversationName}
          otherUserId={selectedConversationOtherUserId}
          accessToken={accessToken}
          currentUserId={currentUser?.id ?? 0}
          onViewProfile={handleViewProfile}
          refreshKey={messagesRefreshKey}
        />
      )}
      {rightPanelMode === 'profile' && <ProfilePanel accessToken={accessToken} />}
      {rightPanelMode === 'search' && (
        <SearchPanel accessToken={accessToken} onViewProfile={handleViewProfile} />
      )}
      {rightPanelMode === 'newChat' && (
        <NewChatPanel
          accessToken={accessToken}
          onStartChat={handleStartChat}
          onCreateGroup={handleCreateGroup}
          onViewProfile={handleViewProfile}
        />
      )}
      {rightPanelMode === 'pendingRequests' && (
        <PendingRequestsPanel accessToken={accessToken} onViewProfile={handleViewProfile} />
      )}
      {rightPanelMode === 'userInfo' && selectedProfileUserId !== null && (
        <UserInfoPanel userId={selectedProfileUserId} accessToken={accessToken} />
      )}
    </div>
  )
}

export default MainShell
