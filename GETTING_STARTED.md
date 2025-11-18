# Getting Started with Blatam Academy Next.js Platform

This guide will help you get up and running with the Blatam Academy Next.js platform, showcasing all the advanced patterns, hooks, and components.

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18.17 or later
- **npm** 9+ or **yarn** 1.22+ or **pnpm** 8+
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd blatam-academy
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` with your configuration:
   ```env
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your-secret-key-here
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
blatam-academy/
├── app/                          # Next.js App Router
│   ├── api/                     # API routes
│   │   └── contact/            # Contact form API
│   ├── contact/                 # Contact page
│   ├── dashboard/               # Dashboard page
│   ├── examples/                # Examples page
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page
├── components/                   # React components
│   ├── dashboard/               # Dashboard components
│   │   ├── data-table.tsx      # Advanced data table
│   │   ├── metrics-dashboard.tsx # Metrics display
│   │   └── dashboard-content.tsx # Dashboard content
│   ├── examples/                # Examples components
│   │   └── examples-content.tsx # Advanced hooks demo
│   ├── layout/                  # Layout components
│   │   ├── header.tsx          # Navigation header
│   │   ├── footer.tsx          # Site footer
│   │   └── mobile-nav.tsx      # Mobile navigation
│   ├── providers/               # Context providers
│   │   ├── theme-provider.tsx   # Theme management
│   │   └── query-provider.tsx   # React Query setup
│   ├── sections/                # Page sections
│   │   ├── hero-section.tsx     # Hero banner
│   │   ├── features-section.tsx # Features grid
│   │   ├── stats-section.tsx    # Statistics display
│   │   ├── cta-section.tsx      # Call to action
│   │   └── contact-form.tsx     # Contact form
│   └── ui/                      # UI components
│       ├── button.tsx           # Button variants
│       ├── card.tsx             # Card layouts
│       ├── input.tsx            # Form inputs
│       ├── badge.tsx            # Status badges
│       ├── tabs.tsx             # Tab navigation
│       └── loading-spinner.tsx  # Loading states
├── hooks/                        # Custom React hooks
│   ├── use-local-storage.ts     # Local storage management
│   ├── use-debounce.ts          # Debounced values
│   ├── use-form-validation.ts   # Form validation
│   └── use-data-fetching.ts     # Data fetching
├── lib/                          # Utility libraries
│   └── utils.ts                 # Common utilities
├── styles/                       # Global styles
│   └── globals.css              # Tailwind CSS setup
├── tests/                        # Test files
│   ├── button.test.tsx          # Button component tests
│   └── examples.test.tsx        # Examples component tests
├── types/                        # TypeScript types
│   └── index.ts                 # Type definitions
├── .eslintrc.json               # ESLint configuration
├── .prettierrc.json             # Prettier configuration
├── jest.config.js               # Jest configuration
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
└── package.json                 # Dependencies and scripts
```

## 🎯 Available Pages

### 1. **Home Page** (`/`)
- Hero section with call-to-action
- Features showcase
- Statistics display
- Contact form integration

### 2. **Dashboard** (`/dashboard`)
- **Metrics Dashboard**: Key performance indicators
- **Data Tables**: Sortable, filterable, searchable tables
- **User Management**: Sample user data with CRUD operations
- **Order Management**: Sample order tracking system

### 3. **Examples** (`/examples`)
- **Local Storage Hook**: Persistent state management
- **Debounce Hook**: Optimized input handling
- **Form Validation Hook**: Advanced form validation with Zod
- **Data Fetching Hook**: Robust API integration

### 4. **Contact** (`/contact`)
- Interactive contact form
- Form validation and submission
- API integration example
- FAQ section

## 🔧 Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Testing
npm run test         # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage
npm run test:e2e     # Run end-to-end tests

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run format       # Format code with Prettier
npm run format:check # Check code formatting

# Type Checking
npm run type-check   # Run TypeScript compiler check
```

## 🎨 Design System

### Color Palette
The platform uses a comprehensive color system with CSS variables:
- **Primary**: Brand colors and main actions
- **Secondary**: Supporting elements
- **Accent**: Highlighting and emphasis
- **Muted**: Backgrounds and subtle text
- **Destructive**: Errors and warnings

### Component Variants
All UI components support multiple variants:
- **Button**: default, destructive, outline, secondary, ghost, link, gradient
- **Card**: default, elevated, outline, ghost, destructive
- **Badge**: default, secondary, destructive, outline, success, warning, info

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Flexible grid systems
- Touch-friendly interactions

## 🧪 Testing Strategy

### Unit Tests
- **Components**: Render testing, user interactions, state changes
- **Hooks**: Custom hook behavior, state management
- **Utilities**: Function logic, edge cases

### Integration Tests
- **Form Submissions**: Complete user workflows
- **API Integration**: Data fetching and error handling
- **Navigation**: Page routing and state persistence

### Test Coverage
- **Target**: 80% coverage minimum
- **Areas**: Branches, functions, lines, statements
- **Tools**: Jest, React Testing Library

## 🚀 Advanced Features

### 1. **Custom Hooks**
- **useLocalStorage**: Persistent state with automatic sync
- **useDebounce**: Optimized input handling
- **useFormValidation**: Zod-based form validation
- **useDataFetching**: Caching, retry logic, optimistic updates

### 2. **Performance Optimizations**
- **Dynamic Imports**: Code splitting with Suspense
- **Image Optimization**: WebP/AVIF formats, lazy loading
- **Bundle Optimization**: Tree shaking, minification
- **Caching**: React Query, local storage, API responses

### 3. **Security Features**
- **Input Validation**: Zod schemas, sanitization
- **Rate Limiting**: API protection, spam prevention
- **Security Headers**: CSP, XSS protection
- **Authentication**: NextAuth.js integration

### 4. **Accessibility**
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Focus Management**: Proper focus indicators
- **Semantic HTML**: Meaningful structure

## 🔌 API Integration

### Contact Form API (`/api/contact`)
```typescript
POST /api/contact
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry",
  "message": "Hello, I have a question..."
}
```

**Features:**
- Zod validation
- Rate limiting (5 requests per minute)
- Honeypot spam protection
- Secure error responses

### External API Example
The examples page demonstrates integration with JSONPlaceholder:
```typescript
const { data, loading, error } = useDataFetching(
  'https://jsonplaceholder.typicode.com/posts',
  postSchema,
  { cacheTime: 10 * 60 * 1000 }
);
```

## 🎯 Development Workflow

### 1. **Feature Development**
```bash
# Create feature branch
git checkout -b feature/new-component

# Make changes and test
npm run test
npm run lint
npm run type-check

# Commit with conventional format
git commit -m "feat: add new dashboard component"

# Push and create PR
git push origin feature/new-component
```

### 2. **Code Quality Checks**
```bash
# Pre-commit hooks (automatic)
npm run lint:fix
npm run format
npm run type-check

# Manual checks
npm run test:coverage
npm run build
```

### 3. **Testing Strategy**
```bash
# Run specific test files
npm test -- --testPathPattern=button

# Run tests with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

## 🚀 Deployment

### Production Build
```bash
# Build the application
npm run build

# Start production server
npm run start

# Or use PM2 for process management
pm2 start npm --name "blatam-academy" -- start
```

### Environment Variables
Ensure these are set in production:
```env
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=your-production-secret
```

### Docker Support
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🎓 Learning Resources

### Next.js
- [Next.js Documentation](https://nextjs.org/docs)
- [App Router Guide](https://nextjs.org/docs/app)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)

### React
- [React Documentation](https://react.dev)
- [Hooks Reference](https://react.dev/reference/react)
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro)

### TypeScript
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [React with TypeScript](https://react-typescript-cheatsheet.netlify.app)

### Tailwind CSS
- [Tailwind Documentation](https://tailwindcss.com/docs)
- [Component Examples](https://tailwindui.com)

## 🤝 Contributing

### Code Standards
- **TypeScript**: Strict mode, proper typing
- **ESLint**: Code quality rules
- **Prettier**: Consistent formatting
- **Conventional Commits**: Standard commit messages

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Ensure all checks pass
5. Submit pull request
6. Code review and merge

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)

## 🎉 What's Next?

Now that you have the platform running, explore:

1. **Dashboard Components**: Try the data tables and metrics
2. **Advanced Hooks**: Experiment with the custom hooks
3. **Form Validation**: Test the contact form
4. **API Integration**: See the data fetching in action
5. **Customization**: Modify themes, colors, and components

Happy coding! 🚀





