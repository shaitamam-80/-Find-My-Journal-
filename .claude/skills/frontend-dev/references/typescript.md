# TypeScript Patterns for React

## Basic Types

### Component Props

```tsx
// Simple props
interface ButtonProps {
  label: string
  onClick: () => void
  disabled?: boolean  // Optional
}

// With children
interface CardProps {
  title: string
  children: React.ReactNode
}

// Extending HTML elements
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
}

// Omitting specific props
interface CustomButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onClick'> {
  onPress: () => void
}
```

### Event Handlers

```tsx
// Form events
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault()
}

// Input change
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value)
}

// Select change
const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
  setOption(e.target.value)
}

// Click event
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  console.log(e.currentTarget)
}

// Keyboard event
const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') submit()
}
```

### State Types

```tsx
// Simple state
const [count, setCount] = useState<number>(0)
const [name, setName] = useState<string>('')
const [isOpen, setIsOpen] = useState<boolean>(false)

// Object state
interface User {
  id: string
  name: string
  email: string
}
const [user, setUser] = useState<User | null>(null)

// Array state
interface Todo {
  id: string
  text: string
  done: boolean
}
const [todos, setTodos] = useState<Todo[]>([])

// Record/Map state
const [errors, setErrors] = useState<Record<string, string>>({})
```

## Generic Patterns

### Generic Component

```tsx
interface ListProps<T> {
  items: T[]
  renderItem: (item: T) => React.ReactNode
  keyExtractor: (item: T) => string
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  )
}

// Usage
<List
  items={users}
  renderItem={user => <span>{user.name}</span>}
  keyExtractor={user => user.id}
/>
```

### Generic Hook

```tsx
function useFetch<T>(url: string): {
  data: T | null
  loading: boolean
  error: Error | null
} {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [url])

  return { data, loading, error }
}

// Usage
const { data, loading } = useFetch<User[]>('/api/users')
```

## Utility Types

### Partial & Required

```tsx
interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

// All optional
type UserUpdate = Partial<User>

// All required
type CompleteUser = Required<User>

// Pick specific
type UserPreview = Pick<User, 'id' | 'name'>

// Omit specific
type UserWithoutId = Omit<User, 'id'>
```

### Union Types

```tsx
// String literals
type Status = 'idle' | 'loading' | 'success' | 'error'

// With type guards
interface LoadingState {
  status: 'loading'
}

interface SuccessState<T> {
  status: 'success'
  data: T
}

interface ErrorState {
  status: 'error'
  error: string
}

type AsyncState<T> = LoadingState | SuccessState<T> | ErrorState

// Usage with narrowing
function renderState<T>(state: AsyncState<T>) {
  switch (state.status) {
    case 'loading':
      return <Spinner />
    case 'success':
      return <Data data={state.data} />  // TypeScript knows data exists
    case 'error':
      return <Error message={state.error} />  // TypeScript knows error exists
  }
}
```

## API Response Types

### Supabase Types

```tsx
// Generate with: npx supabase gen types typescript > src/types/database.ts

import type { Database } from '@/types/database'

// Table row type
type Profile = Database['public']['Tables']['profiles']['Row']

// Insert type (without auto-generated fields)
type ProfileInsert = Database['public']['Tables']['profiles']['Insert']

// Update type (all fields optional)
type ProfileUpdate = Database['public']['Tables']['profiles']['Update']

// Usage
const { data } = await supabase
  .from('profiles')
  .select('*')
  .single()

// data is typed as Profile | null
```

### API Response Pattern

```tsx
// Generic API response
interface ApiResponse<T> {
  data: T | null
  error: string | null
  status: number
}

// Paginated response
interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

// Usage
async function fetchJournals(query: string): Promise<ApiResponse<Journal[]>> {
  try {
    const res = await fetch(`/api/journals?q=${query}`)
    const data = await res.json()
    return { data, error: null, status: res.status }
  } catch (err) {
    return { data: null, error: 'Failed to fetch', status: 500 }
  }
}
```

## Context Types

```tsx
interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

// Custom hook with type guard
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
```

## Form Types

### Form Values

```tsx
interface SearchFormValues {
  title: string
  abstract: string
  keywords: string[]
}

// With validation
interface FormErrors {
  [K in keyof SearchFormValues]?: string
}

function validateForm(values: SearchFormValues): FormErrors {
  const errors: FormErrors = {}
  
  if (!values.title) {
    errors.title = 'Title is required'
  }
  
  if (values.abstract.length < 50) {
    errors.abstract = 'Abstract must be at least 50 characters'
  }
  
  return errors
}
```

### React Hook Form

```tsx
import { useForm, SubmitHandler } from 'react-hook-form'

interface FormInputs {
  title: string
  abstract: string
}

function SearchForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormInputs>()
  
  const onSubmit: SubmitHandler<FormInputs> = (data) => {
    console.log(data.title)  // Typed as string
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('title', { required: true })} />
      {errors.title && <span>Required</span>}
    </form>
  )
}
```

## Common Patterns

### Type Assertions

```tsx
// When you know better than TypeScript
const input = document.getElementById('search') as HTMLInputElement
input.value = 'test'

// Non-null assertion (use sparingly)
const user = getUser()!  // Assert not null

// Better: type guard
if (user) {
  console.log(user.name)  // TypeScript knows user exists
}
```

### Type Guards

```tsx
// Custom type guard
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj
  )
}

// Usage
const data = await fetchData()
if (isUser(data)) {
  console.log(data.name)  // Typed as User
}
```

### Const Assertions

```tsx
// Without const
const colors = ['red', 'green', 'blue']  // string[]

// With const
const colors = ['red', 'green', 'blue'] as const  // readonly ['red', 'green', 'blue']
type Color = typeof colors[number]  // 'red' | 'green' | 'blue'

// Object const
const config = {
  api: 'https://api.example.com',
  timeout: 5000
} as const
// config.api is 'https://api.example.com', not string
```

## Debugging Tips

```tsx
// Check inferred type
const x = someFunction()
type X = typeof x  // Hover to see type

// Satisfies operator (TS 4.9+)
const config = {
  theme: 'dark',
  language: 'en'
} satisfies Record<string, string>
// Preserves literal types while checking structure

// Quick any escape hatch (avoid in production)
(value as any).unknownProperty
```
