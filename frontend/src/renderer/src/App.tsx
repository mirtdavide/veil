import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import MainShell from './pages/Mainshell'

type View = 'login' | 'register' | 'shell'

function App(): React.JSX.Element {

  interface CurrentUser {
    id: number
    username: string
    email: string
  }
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const [view, setView] = useState<View>('login')
  const [accessToken, setAccessToken] = useState<string | null>(null)
  async function handleLogin(email: string, password: string): Promise<void> {
    const response = await fetch('http://127.0.0.1:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    if (!response.ok) {
      console.log('login fallito', response.status)
      return
    }

    const data = await response.json()
    setAccessToken(data.access_token)

    const meResponse = await fetch('http://127.0.0.1:8000/auth/me', {
    headers: { Authorization: `Bearer ${data.access_token}` }
    })
    const me = await meResponse.json()
    setCurrentUser(me)
    setView('shell')
  }

  function handleRegister(
    username: string,
    email: string,
    password: string,
    inviteCode: string
  ): void {
    console.log('register da App', username, email, password, inviteCode)
    setView('login') // Switch to the login view after successful registration
  }

  if (view === 'login') {
    return <LoginPage onLogin={handleLogin} onNavigateToRegister={() => setView('register')} />
  }

  if (view === 'register') {
    return <RegisterPage onRegister={handleRegister} onNavigateToLogin={() => setView('login')} />
  }


  return <MainShell accessToken={accessToken} currentUser={currentUser} />
}

export default App