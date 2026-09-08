import IconRail from '../components/IconRail'
import Sidebar from '../components/Sidebar'



function Mainshell(): React.JSX.Element {

    function handleOpenProfile(): void {
        console.log('Profile button clicked')
    }
    function handleOpenSearch(): void {
        console.log('Search button clicked')
    }
    function handleSelectConversation(conversationId: number): void {
        console.log(`Selected conversation with ID: ${conversationId}`)
    }
    function handleNewConversation(): void {
        console.log('New conversation button clicked')
    }
    

    return (


        <div className="flex">
            <IconRail onOpenProfile={handleOpenProfile} onOpenSearch={handleOpenSearch} />
            <Sidebar onSelectConversation={handleSelectConversation} onNewConversation={handleNewConversation} />
            <div className="flex-1 bg-bg h-screen flex items-center justify-center">
                <p className="text-text-muted text-sm">Content on the right side</p>

            </div>
        </div>
    )
    


}

export default Mainshell