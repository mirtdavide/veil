
//FunctionsOfTheButtons, need to add the functions to the signature of function PendingRequestsPanel
interface PendingRequestsPanelProps{

    //NameOfTheFunction:Input:inWhichFormIsTheInput=>WhatIsReturned
    onAcceptRequest:(requestId: number) => void
    onRefuseRequest:(requestId: number) => void

}


//Data of a request, id is the corresponding id of the request in the DB, username as well corresponds to the username
interface Request {
  id: number
  username: string
}

//Mock requests to test the mapping
const requests: Request[] = [
  { id: 1, username: 'ivin' },
  { id: 2, username: 'luchino' }
]





function PendingRequestsPanel({ onAcceptRequest, onRefuseRequest }: PendingRequestsPanelProps): React.JSX.Element {
    return(
    <div className="flex flex-1 flex-col bg-bg h-screen items-center justify-start gap-2 p-2">

        {requests.map((request) => (
        
        <div key={request.id} className="flex justify-between items-center w-full px-3 py-2 bg-bg-secondary rounded">
            <div className="flex gap-3 items-center">
                <div className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold text-sm"></div>
                <p className="text-text">{request.username}</p>
            </div>
            <div className="flex gap-3">
                {/* onClick={onAcceptRequest} would NOT pass request.id — React calls the
                    handler automatically on click with the browser's MouseEvent as the
                    first argument, since that's what onClick always hands over by default.
                    Wrapping it in an arrow function lets us decide what gets passed instead:
                    onClick={() => onAcceptRequest(request.id)} calls OUR function on click,
                    which then calls onAcceptRequest with request.id, not the event. */}
                <button
                onClick={() => onAcceptRequest(request.id)}
                className="bg-accent hover:bg-accent-hover text-text text-sm rounded px-3 py-1">
                    Accetta
                </button>
                <button
                onClick={() => onRefuseRequest(request.id)}
                className="border border-bg-tertiary text-text text-sm rounded px-3 py-1">
                    Rfifuta
                </button>
            </div>
        </div>
        ))}
        
        
    </div>
    )

    
}

export default PendingRequestsPanel