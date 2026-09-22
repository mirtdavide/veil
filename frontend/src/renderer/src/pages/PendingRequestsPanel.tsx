

import {useEffect, useState} from 'react'

//Data of a request modeled after the backend, id is the corresponding id of the request in the DB, username as well corresponds to the username

interface Request{

  id: number
  requester: {
    id: number
    username: string
  }
  created_at: string

}





//Functions Of The Buttons, need to add the functions to the signature of function PendingRequestsPanel
interface PendingRequestsPanelProps{
    accessToken: string | null
    //NameOfTheFunction:Input:inWhichFormIsTheInput=>WhatIsReturned
    

}




function PendingRequestsPanel({ accessToken }: PendingRequestsPanelProps): React.JSX.Element {
    //Again give the variables a memory after each redraw, will contain an array of <Request>, initial value ([]) set to empty
    //The useState function returns 2 things, the values of the state and a function to change them
    const [requests, setRequests] = useState<Request[]>([])

    //When the component appears on screen/is redrawn this code is executed
    //useEffect(A,B)
    // A = () => {} The function to be called at every redraw
    // B = [], an array, at every redraw what you put inside is confronted: previous redraw content == current redraw content? 
    //if yes then we will not call again the A function, else we will
    //In our case empty is compared with empty so the A function will not be recalled
    useEffect(() => {

        //We need to await a result from the server so async function, Promise label as an async functiona always returns a promise
        async function loadRequests(): Promise<void> {
            //GET endpoint for the pending requests, we need to await the result
            const response = await fetch('http://127.0.0.1:8000/connections/pending', {
                headers: { Authorization: `Bearer ${accessToken}` }
            })

            if (!response.ok) {
                console.log('Error while loading the requests', response.status)
                return
            }

           
            const data = await response.json()
            setRequests(data)
        }

        loadRequests()
    }, [])

    async function handleAccept(requestID: number): Promise<void>{

        const response = await fetch(`http://127.0.0.1:8000/connections/${requestID}/accept`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${accessToken}` }
        })

        if (!response.ok) {
                console.log('Error while accepting the request', response.status)
                return
            }
        //Filter function, goes through each element, if condition is true element is kept, else removed
        setRequests(requests.filter((request) => request.id !== requestID))



    }

    async function handleReject(requestID: number): Promise<void>{

        const response = await fetch(`http://127.0.0.1:8000/connections/${requestID}/reject`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${accessToken}` }
        })

        if (!response.ok) {
                console.log('Error while refusing the request', response.status)
                return
            }
        
        setRequests(requests.filter((request) => request.id !== requestID))



    }

    return(
    
    <div className="flex flex-1 flex-col bg-bg h-screen items-center justify-start gap-2 p-2">

        {requests.map((request) => (
        
        <div key={request.id} className="flex justify-between items-center w-full px-3 py-2 bg-bg-secondary rounded">
            <div className="flex gap-3 items-center">
                <div className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold text-sm"></div>
                <p className="text-text">{request.requester.username}</p>
            </div>
            <div className="flex gap-3">
                {/* onClick={onAcceptRequest} would NOT pass request.id — React calls the
                    handler automatically on click with the browser's MouseEvent as the
                    first argument, since that's what onClick always hands over by default.
                    Wrapping it in an arrow function lets us decide what gets passed instead:
                    onClick={() => onAcceptRequest(request.id)} calls OUR function on click,
                    which then calls onAcceptRequest with request.id, not the event. */}
                <button
                onClick={() =>  handleAccept(request.id)}
                className="bg-accent hover:bg-accent-hover text-text text-sm rounded px-3 py-1">
                    Accetta
                </button>
                <button
                onClick={() => handleReject(request.id)}
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