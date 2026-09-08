import { useState, type SubmitEvent } from 'react'

interface RegisterPageProps {
onRegister: (username: string, email: string, password: string, inviteCode: string) => void
    onNavigateToLogin: () => void
}


function RegisterPage({ onRegister, onNavigateToLogin }: RegisterPageProps): React.JSX.Element {

    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [inviteCode, setInviteCode] = useState('')
    /*State variable to store the error message, and a function to update that value when the user types in the input field (called by the onChange event).
    It can take either a string or null, and is initialized to null. 
    This is used to display an error message if the passwords do not match when the user submits the form. 
    */
    
    const [error, setError] = useState<string | null>(null)

    function handleSubmit(e: SubmitEvent<HTMLFormElement>): void {
    e.preventDefault()
    if (password !== confirmPassword) {
      setError('Le password non coincidono')
      return
    }
    setError(null)
    onRegister(username, email, password, inviteCode)
    }
    return(
      <div className="min-h-screen flex items-center justify-center bg-bg text-text">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
        />
         <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Conferma password"
          className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
        />
        {
        //Conditional rendering: if error is not null, render the paragraph element with the error message. If error is null, render nothing.
        error && <p className="text-red-400 text-sm text-center">{error}</p>
        }

        <input
          type="text"
          value={inviteCode}
          onChange={(e) => setInviteCode(e.target.value)}
          placeholder="Codice invito"
          className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
        />
        <button
          type="submit"
          className="bg-accent hover:bg-accent-hover text-text rounded py-2 font-semibold"
        >
          Registrati
        </button>
        <p className="text-text-muted text-sm text-center">
          Hai già un account?{' '}
          <span
            onClick={onNavigateToLogin}
            className="text-accent cursor-pointer hover:underline"
          >
            Accedi
          </span>
        </p>
      </form>
    </div>
    )



}

export default RegisterPage