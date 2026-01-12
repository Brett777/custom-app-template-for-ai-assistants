# UI Design Guide for DataRobot Custom Applications

This document provides comprehensive guidance for designing and building user interfaces for DataRobot Custom Applications. It covers the design system, component library, theming, and best practices.

> **IMPORTANT: Use DataRobot UI (dr-ui) as the default component library for all UI development unless explicitly stated otherwise.** dr-ui extends shadcn/ui with DataRobot-specific components, theming, and features like production-ready chat interfaces.

## Table of Contents
1. [Design System Overview](#design-system-overview)
2. [Technology Stack](#technology-stack)
3. [DataRobot UI (dr-ui) - Default Library](#datarobot-ui-dr-ui)
4. [Component Library (shadcn/ui)](#component-library-shadcnui)
5. [Theming and CSS Variables](#theming-and-css-variables)
6. [Color System](#color-system)
7. [Typography](#typography)
8. [Spacing and Layout](#spacing-and-layout)
9. [Component Patterns](#component-patterns)
10. [Chat Interface Design](#chat-interface-design)
11. [Dark Mode](#dark-mode)
12. [Accessibility](#accessibility)
13. [Best Practices](#best-practices)

---

## Design System Overview

This template uses a modern design system built on:
- **DataRobot UI (dr-ui)** - Primary component library (DEFAULT CHOICE)
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Base components (extended by dr-ui)
- **Radix UI** - Unstyled, accessible component primitives
- **CSS Variables** - Theme tokens for consistent styling

### Component Selection Priority

**Always follow this order when choosing components:**

1. **dr-ui component** - Use if available (chat, buttons, cards, forms, etc.)
2. **shadcn/ui component** - Use only if dr-ui doesn't have the component
3. **Custom component** - Build only when necessary, following dr-ui patterns

### Design Principles

1. **Consistency** - Use design tokens for colors, spacing, and typography
2. **Accessibility** - Follow WCAG guidelines, use semantic HTML
3. **Responsiveness** - Mobile-first design approach
4. **Performance** - Minimize CSS, use Tailwind's purging

---

## Technology Stack

### Frontend
```
React 19.x          - UI library
TypeScript 5.x      - Type safety
Vite 7.x            - Build tool
Tailwind CSS 4.x    - Utility CSS
shadcn/ui           - Component library
Radix UI            - Accessible primitives
```

### Key Files
| File | Purpose |
|------|---------|
| `frontend/src/index.css` | CSS variables and Tailwind layers |
| `frontend/tailwind.config.js` | Tailwind configuration |
| `frontend/src/lib/utils.ts` | Utility functions (cn, etc.) |
| `frontend/src/components/ui/` | shadcn/ui components |

---

## Component Library (shadcn/ui)

This template uses [shadcn/ui](https://ui.shadcn.com/), a collection of accessible, customizable components.

### Installing Components

```bash
cd frontend

# Add individual components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add toast

# View all available components
npx shadcn-ui@latest add
```

### Available Components

**Form Controls:**
- `button` - Buttons with variants (primary, secondary, destructive, ghost, link)
- `input` - Text inputs
- `textarea` - Multi-line text
- `checkbox` - Checkboxes
- `radio-group` - Radio buttons
- `select` - Dropdowns
- `switch` - Toggle switches
- `slider` - Range sliders

**Layout:**
- `card` - Content containers
- `separator` - Visual dividers
- `scroll-area` - Scrollable containers
- `sheet` - Slide-out panels
- `tabs` - Tabbed navigation

**Feedback:**
- `alert` - Alert messages
- `badge` - Status indicators
- `progress` - Progress bars
- `skeleton` - Loading placeholders
- `toast` - Notifications

**Overlay:**
- `dialog` - Modal dialogs
- `dropdown-menu` - Dropdown menus
- `popover` - Popovers
- `tooltip` - Tooltips

### Using Components

```tsx
// Import components
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

// Use in JSX
function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Settings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input placeholder="Enter value..." />
        <Button>Save Changes</Button>
      </CardContent>
    </Card>
  )
}
```

---

## DataRobot UI (dr-ui) - Default Library

> **dr-ui is the default component library for all DataRobot Custom Applications.** Use it for all UI development unless explicitly stated otherwise.

[dr-ui](https://dr-ui.datarobot.com/) is DataRobot's open-source React component library that extends shadcn/ui with DataRobot-specific features and theming.

### Why dr-ui is the Default

| Reason | Description |
|--------|-------------|
| **DataRobot Theming** | Consistent look and feel with DataRobot products |
| **Chat Components** | Production-ready chat interfaces for AI agents |
| **Extended shadcn/ui** | All shadcn/ui benefits plus DataRobot enhancements |
| **Accessibility** | Built on Radix UI primitives |
| **i18n Support** | Multiple language locales |

### Key Features

- **Chat Components** - Complete chat interface with message handling
- **Custom Hooks** - `use-chat` for managing chat functionality
- **Accessibility** - Built on Radix UI primitives
- **i18n Support** - Multiple language locales
- **Dark Mode** - Flexible theming system

### Installation

```bash
# Configure components.json to use dr-ui registry
npx shadcn@latest add @dr-ui/button
npx shadcn@latest add @dr-ui/chat
```

### Chat Components

dr-ui provides production-ready chat components:

```tsx
import { Chat, ChatMessage, ChatInput } from '@dr-ui/chat'
import { useChat } from '@dr-ui/hooks'

function ChatInterface() {
  const { messages, sendMessage, isLoading } = useChat({
    endpoint: '/api/v1/agent/chat'
  })

  return (
    <Chat>
      {messages.map(msg => (
        <ChatMessage key={msg.id} role={msg.role}>
          {msg.content}
        </ChatMessage>
      ))}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </Chat>
  )
}
```

---

## Theming and CSS Variables

### CSS Variable System

The design system uses HSL-based CSS variables for theming:

```css
/* frontend/src/index.css */
:root {
  /* Background colors */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;

  /* Card colors */
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;

  /* Primary colors (buttons, links) */
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;

  /* Secondary colors */
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;

  /* Muted colors (disabled, subtle) */
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;

  /* Accent colors (highlights) */
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;

  /* Destructive colors (errors, delete) */
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;

  /* Border and input */
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;

  /* Border radius */
  --radius: 0.5rem;
}
```

### Using CSS Variables

```tsx
// In Tailwind classes
<div className="bg-background text-foreground">
  <button className="bg-primary text-primary-foreground">
    Click me
  </button>
</div>

// In custom CSS
.custom-element {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
}
```

---

## Color System

### Semantic Color Tokens

| Token | Usage |
|-------|-------|
| `background` | Page/app background |
| `foreground` | Main text color |
| `primary` | Primary actions, links |
| `secondary` | Secondary actions |
| `muted` | Disabled states, subtle elements |
| `accent` | Highlights, focus states |
| `destructive` | Errors, delete actions |
| `card` | Card backgrounds |
| `popover` | Dropdown/popover backgrounds |
| `border` | Borders, dividers |
| `input` | Form input borders |
| `ring` | Focus rings |

### DataRobot Brand Colors

For DataRobot-branded applications, consider these colors:

```css
:root {
  /* DataRobot Blue */
  --dr-blue-50: 210 100% 97%;
  --dr-blue-100: 210 100% 93%;
  --dr-blue-500: 210 100% 50%;
  --dr-blue-600: 210 100% 45%;
  --dr-blue-700: 210 100% 35%;

  /* DataRobot Green (Success) */
  --dr-green-500: 142 76% 36%;

  /* DataRobot Red (Error) */
  --dr-red-500: 0 84% 60%;

  /* DataRobot Yellow (Warning) */
  --dr-yellow-500: 45 93% 47%;
}
```

---

## Typography

### Font Stack

```css
/* System font stack for performance */
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
             "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

/* Monospace for code */
font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
             "Liberation Mono", "Courier New", monospace;
```

### Font Sizes (Tailwind)

| Class | Size | Use Case |
|-------|------|----------|
| `text-xs` | 0.75rem (12px) | Captions, labels |
| `text-sm` | 0.875rem (14px) | Secondary text, metadata |
| `text-base` | 1rem (16px) | Body text |
| `text-lg` | 1.125rem (18px) | Large body text |
| `text-xl` | 1.25rem (20px) | Subheadings |
| `text-2xl` | 1.5rem (24px) | Section headings |
| `text-3xl` | 1.875rem (30px) | Page headings |
| `text-4xl` | 2.25rem (36px) | Hero headings |

### Font Weights

| Class | Weight | Use Case |
|-------|--------|----------|
| `font-normal` | 400 | Body text |
| `font-medium` | 500 | Emphasis |
| `font-semibold` | 600 | Headings, buttons |
| `font-bold` | 700 | Strong emphasis |

### Typography Examples

```tsx
// Page heading
<h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>

// Section heading
<h2 className="text-2xl font-semibold">Recent Activity</h2>

// Body text
<p className="text-base text-foreground">Regular content text</p>

// Muted text
<p className="text-sm text-muted-foreground">Secondary information</p>

// Code
<code className="font-mono text-sm bg-muted px-1 rounded">code</code>
```

---

## Spacing and Layout

### Spacing Scale (Tailwind)

| Class | Size | Pixels |
|-------|------|--------|
| `p-1` / `m-1` | 0.25rem | 4px |
| `p-2` / `m-2` | 0.5rem | 8px |
| `p-3` / `m-3` | 0.75rem | 12px |
| `p-4` / `m-4` | 1rem | 16px |
| `p-5` / `m-5` | 1.25rem | 20px |
| `p-6` / `m-6` | 1.5rem | 24px |
| `p-8` / `m-8` | 2rem | 32px |
| `p-10` / `m-10` | 2.5rem | 40px |
| `p-12` / `m-12` | 3rem | 48px |

### Common Layouts

```tsx
// Centered container
<div className="max-w-2xl mx-auto p-8">
  {/* Content */}
</div>

// Card grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card>...</Card>
  <Card>...</Card>
  <Card>...</Card>
</div>

// Flex row with spacing
<div className="flex items-center gap-4">
  <Button>Action 1</Button>
  <Button>Action 2</Button>
</div>

// Vertical stack
<div className="space-y-4">
  <Component1 />
  <Component2 />
  <Component3 />
</div>
```

### Responsive Breakpoints

| Prefix | Min Width | Use Case |
|--------|-----------|----------|
| (none) | 0px | Mobile first |
| `sm:` | 640px | Large phones |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Laptops |
| `xl:` | 1280px | Desktops |
| `2xl:` | 1536px | Large displays |

```tsx
// Responsive example
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* 1 column on mobile, 2 on tablet, 3 on desktop */}
</div>
```

---

## Component Patterns

### Button Variants

```tsx
import { Button } from '@/components/ui/button'

// Primary action
<Button>Submit</Button>

// Secondary action
<Button variant="secondary">Cancel</Button>

// Destructive action
<Button variant="destructive">Delete</Button>

// Ghost button
<Button variant="ghost">More Options</Button>

// Link style
<Button variant="link">Learn More</Button>

// Outline button
<Button variant="outline">Export</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>

// With icon
<Button>
  <PlusIcon className="mr-2 h-4 w-4" />
  Add Item
</Button>

// Loading state
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Loading...
</Button>
```

### Card Patterns

```tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

// Basic card
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description text</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

// Stats card
<Card>
  <CardHeader className="pb-2">
    <CardDescription>Total Revenue</CardDescription>
    <CardTitle className="text-3xl">$45,231.89</CardTitle>
  </CardHeader>
  <CardContent>
    <p className="text-xs text-muted-foreground">
      +20.1% from last month
    </p>
  </CardContent>
</Card>
```

### Form Patterns

```tsx
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

<form className="space-y-4">
  <div className="space-y-2">
    <Label htmlFor="email">Email</Label>
    <Input id="email" type="email" placeholder="email@example.com" />
  </div>

  <div className="space-y-2">
    <Label htmlFor="password">Password</Label>
    <Input id="password" type="password" />
  </div>

  <Button type="submit" className="w-full">
    Sign In
  </Button>
</form>
```

---

## Chat Interface Design

### Chat Layout Structure

```tsx
<div className="flex flex-col h-[600px]">
  {/* Header */}
  <div className="flex-shrink-0 border-b p-4">
    <h2 className="font-semibold">Agent Chat</h2>
  </div>

  {/* Messages area */}
  <div className="flex-1 overflow-y-auto p-4 space-y-4">
    {messages.map(message => (
      <ChatMessage key={message.id} {...message} />
    ))}
  </div>

  {/* Input area */}
  <div className="flex-shrink-0 border-t p-4">
    <ChatInput onSend={handleSend} />
  </div>
</div>
```

### Message Bubbles

```tsx
// User message (right-aligned)
<div className="flex justify-end">
  <div className="max-w-[80%] rounded-lg px-4 py-2 bg-primary text-primary-foreground">
    <p className="whitespace-pre-wrap">{message}</p>
  </div>
</div>

// Assistant message (left-aligned)
<div className="flex justify-start">
  <div className="max-w-[80%] rounded-lg px-4 py-2 bg-muted">
    <p className="whitespace-pre-wrap">{message}</p>
  </div>
</div>

// Loading indicator
<div className="flex justify-start">
  <div className="bg-muted rounded-lg px-4 py-2">
    <div className="flex items-center gap-1">
      <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
      <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.1s]" />
      <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.2s]" />
    </div>
  </div>
</div>
```

### Chat Input

```tsx
<div className="flex gap-2">
  <input
    type="text"
    value={input}
    onChange={(e) => setInput(e.target.value)}
    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
    placeholder="Type your message..."
    className="flex-1 px-3 py-2 bg-background border border-input rounded-md
               text-sm focus:outline-none focus:ring-2 focus:ring-ring"
  />
  <Button onClick={handleSend} disabled={!input.trim()}>
    Send
  </Button>
</div>
```

---

## Dark Mode

### Enabling Dark Mode

The template supports dark mode via the `dark` class on the root element:

```tsx
// Toggle dark mode
document.documentElement.classList.toggle('dark')

// Check if dark mode
const isDark = document.documentElement.classList.contains('dark')
```

### Dark Mode Colors

```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 212.7 26.8% 83.9%;
}
```

### Dark Mode Toggle Component

```tsx
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'

function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)

  const toggleTheme = () => {
    document.documentElement.classList.toggle('dark')
    setIsDark(!isDark)
  }

  return (
    <Button variant="ghost" size="icon" onClick={toggleTheme}>
      {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </Button>
  )
}
```

---

## Accessibility

### Key Principles

1. **Semantic HTML** - Use proper elements (`button`, `nav`, `main`, `article`)
2. **Keyboard Navigation** - All interactive elements accessible via keyboard
3. **Focus Indicators** - Visible focus states (ring utility)
4. **Color Contrast** - Minimum 4.5:1 for text, 3:1 for large text
5. **Screen Readers** - Use ARIA labels where needed

### Focus Styles

```css
/* Default focus ring (from Tailwind) */
.focus-visible:outline-none
.focus-visible:ring-2
.focus-visible:ring-ring
.focus-visible:ring-offset-2
```

### ARIA Labels

```tsx
// Icon-only button
<Button variant="ghost" size="icon" aria-label="Open menu">
  <MenuIcon className="h-5 w-5" />
</Button>

// Loading state
<Button disabled aria-busy="true">
  <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
  Loading...
</Button>

// Chat region
<div role="log" aria-live="polite" aria-label="Chat messages">
  {messages.map(msg => <Message key={msg.id} {...msg} />)}
</div>
```

### Skip Links

```tsx
// Add to top of page
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4
             bg-background px-4 py-2 z-50"
>
  Skip to main content
</a>
```

---

## Best Practices

### Do's

1. **Use semantic color tokens** - `bg-primary` not `bg-blue-500`
2. **Compose with Tailwind utilities** - Avoid custom CSS when possible
3. **Use the `cn()` utility** - For conditional class merging
4. **Follow component patterns** - Consistent structure across the app
5. **Test responsive designs** - Check all breakpoints
6. **Maintain accessibility** - Test with keyboard, screen readers

### Don'ts

1. **Don't use inline styles** - Use Tailwind classes
2. **Don't hardcode colors** - Use CSS variables
3. **Don't skip focus states** - Critical for accessibility
4. **Don't ignore loading states** - Show skeletons/spinners
5. **Don't forget error states** - Handle edge cases
6. **Don't use `!important`** - Use proper specificity

### The `cn()` Utility

```tsx
import { cn } from '@/lib/utils'

// Merge classes conditionally
<button
  className={cn(
    "px-4 py-2 rounded-md", // Base styles
    isActive && "bg-primary text-primary-foreground", // Active state
    isDisabled && "opacity-50 cursor-not-allowed", // Disabled state
    className // Allow overrides from props
  )}
>
  {children}
</button>
```

### File Organization

```
frontend/src/
├── components/
│   ├── ui/              # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── chat/            # Feature-specific components
│   │   └── ChatBot.tsx
│   └── layout/          # Layout components
│       ├── Header.tsx
│       └── Sidebar.tsx
├── lib/
│   ├── utils.ts         # Utility functions
│   └── basePath.ts      # DataRobot path helpers
├── hooks/               # Custom React hooks
│   └── useChat.ts
├── App.tsx
├── main.tsx
└── index.css            # CSS variables and Tailwind
```

---

## For AI Assistants

When building UI for DataRobot Custom Applications:

### Default: Use DataRobot UI (dr-ui)

**ALWAYS use dr-ui as the primary component library unless explicitly stated otherwise.**

### Quick Reference

1. **Add dr-ui components (preferred):**
   ```bash
   cd frontend && npx shadcn@latest add @dr-ui/[component]
   ```

2. **Add shadcn/ui components (fallback only):**
   ```bash
   cd frontend && npx shadcn-ui@latest add [component]
   ```

3. **For chat interfaces - ALWAYS use dr-ui:**
   ```tsx
   import { Chat, ChatMessage, ChatInput } from '@dr-ui/chat'
   import { useChat } from '@dr-ui/hooks'
   ```

4. **Use semantic tokens:**
   ```tsx
   bg-primary, text-foreground, border-border
   ```

5. **Follow patterns in existing components:**
   - Check `frontend/src/components/ui/` for examples
   - Use `cn()` for class merging

6. **DataRobot compatibility:**
   - Always use `apiUrl()` from `@/lib/basePath`
   - Test at `/custom_applications/{id}/` paths

### Component Selection Order

1. **dr-ui** - Check first, use if available
2. **shadcn/ui** - Use only if dr-ui doesn't have it
3. **Custom** - Build only when necessary

### Component Checklist

When creating new components:
- [ ] Uses dr-ui components when available
- [ ] Uses Tailwind utility classes
- [ ] Uses CSS variable tokens for colors
- [ ] Has proper TypeScript types
- [ ] Handles loading states
- [ ] Handles error states
- [ ] Accessible (keyboard, ARIA)
- [ ] Responsive design
- [ ] Supports dark mode
