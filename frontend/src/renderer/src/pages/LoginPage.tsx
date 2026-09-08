//Component memory across renders, it means that the field values will be preserved between renders of the component.
import { useState, type SubmitEvent } from 'react'


interface LoginPageProps {
  onLogin: (email: string, password: string) => void
  onNavigateToRegister: () => void
}
function LoginPage({ onLogin, onNavigateToRegister }: LoginPageProps): React.JSX.Element {

    //Variable to store the email input value, and a function to update that value when the user types in the input field (called by the onChange event).
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    function handleSubmit(e: SubmitEvent<HTMLFormElement>): void {
    e.preventDefault()
    onLogin(email, password)
    }
    return(
      <div className="min-h-screen flex items-center justify-center bg-bg text-text">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
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
        <button
          type="submit"
          className="bg-accent hover:bg-accent-hover text-text rounded py-2 font-semibold"
        >
          Accedi
        </button>
        <p className="text-text-muted text-sm text-center">
          Non hai un account?{' '}
          <span
            onClick={onNavigateToRegister}
            className="text-accent cursor-pointer hover:underline"
          >
            Registrati
          </span>
        </p>
      </form>
    </div>
  )
    

}


/*This makes the LoginPage function available for import in other files, such as App.tsx. 
Without this export statement, the LoginPage function would be private to this file and could not be used elsewhere in the application.
*/
export default LoginPage