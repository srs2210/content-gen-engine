# Getting Started

### Running the Application Locally
  *   Navigate to the frontend folder and run `yarn install` to download and install project dependancies
  *   From the frontend folder and run `yarn dev` - this will start the development server locally

### Deploying to Production

  *   Update your `PROJECT_ID` and `CLOUDRUN_SERVICE_NAME` in the `deploy.sh` file.
  *   From the frontend folder, make the deployment script executable using `chmod +x ./scripts/deploy.sh`, then run `./scripts/deploy.sh` to deploy.

## Adding new templates

To add new templates, you need to create template entries directly in Firestore (see readme file in `fastapi-backend` for more details).

After you have added more templates,
- in line 41 of `src/types.ts`, update the `AspectRatio` enum to include the new templates
- in line 105 of `src/components/ConfigurePostForm.tsx`, update the aspect ratio options to include the new templates

## Overview of the project

This is a social media content generation application built with React + TypeScript + Vite that helps users generate and manage social media posts. The application consists of several key components:

### Architecture
- Frontend: React + TypeScript + Vite
- Backend: Python FastAPI
- Storage: Google Cloud Firestore
- Image Processing: Cloud Functions
- Message Queue: Google Cloud Pub/Sub

### Key Features
1. **Post Generation**
   - Users can create new post requests with customizable parameters
   - Supports multiple aspect ratios and art styles
   - Configurable post count and social media platform targeting

2. **User Management**
   - User authentication and authorization
   - Personalized sign-off management
   - User-specific post history

3. **Content Review**
   - Post evaluation and compliance checking
   - Vote system for generated content
   - Download capabilities for approved posts

### Main Components
- **GeneratePost**: Main workflow component for creating new posts
- **ConfigurePostForm**: Form component for post configuration
- **GeneratedPost**: Display component for viewing generated posts
- **WorkflowStages**:
  - Configure Post
  - View Generated Posts

### Integration Points
- Communicates with FastAPI backend for post generation and management
- Integrates with Google Cloud services for storage and processing
- Supports multiple social media platform requirements for caption generation

### Development Guidelines
- Follow TypeScript type definitions in `src/types.ts`
- Use provided API service for backend communication
- Maintain consistent error handling using the utility functions
- Follow the established component structure for new features

This application is designed to be scalable and maintainable, with clear separation of concerns and type safety throughout the codebase.

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default {
  // other rules...
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    project: ["./tsconfig.json", "./tsconfig.node.json"],
    tsconfigRootDir: __dirname,
  },
};
```

- Replace `plugin:@typescript-eslint/recommended` to `plugin:@typescript-eslint/recommended-type-checked` or `plugin:@typescript-eslint/strict-type-checked`
- Optionally add `plugin:@typescript-eslint/stylistic-type-checked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and add `plugin:react/recommended` & `plugin:react/jsx-runtime` to the `extends` list
