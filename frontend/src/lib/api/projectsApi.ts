import { api } from './apiSlice'
import type { Project, ProjectComponent, ProjectWithComponents, CreateProjectRequest } from '@/types/project'

// ---------------------------------------------------------------------------
// Backend response shapes (snake_case from the API)
// ---------------------------------------------------------------------------

interface BackendComponent {
  id: string
  project_id: string
  name: string
  description?: string | null
  sort_order: number
  nodes: ProjectComponent['nodes']
  edges: ProjectComponent['edges']
  scene_root?: ProjectComponent['sceneRoot']
  created_at: string
  updated_at: string
}

interface BackendProjectWithComponents {
  id: string
  owner_id: string
  name: string
  description?: string | null
  status: string
  components: BackendComponent[]
  created_at: string
  updated_at: string
}

// ---------------------------------------------------------------------------
// Save request shape (snake_case for the API)
// ---------------------------------------------------------------------------

interface ComponentSavePayload {
  id?: string
  name: string
  description?: string
  sort_order: number
  nodes: ProjectComponent['nodes']
  edges: ProjectComponent['edges']
  scene_root?: ProjectComponent['sceneRoot']
}

export interface SaveProjectComponentsRequest {
  projectId: string
  components: ComponentSavePayload[]
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mapBackendComponent(c: BackendComponent): ProjectComponent {
  return {
    id: c.id,
    name: c.name,
    description: c.description ?? undefined,
    nodes: c.nodes,
    edges: c.edges,
    sceneRoot: c.scene_root ?? undefined,
  }
}

function mapBackendProjectWithComponents(raw: BackendProjectWithComponents): ProjectWithComponents {
  return {
    id: raw.id,
    name: raw.name,
    components: raw.components.map(mapBackendComponent),
  }
}

// ---------------------------------------------------------------------------
// RTK Query endpoints
// ---------------------------------------------------------------------------

export const projectsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getProjects: builder.query<Project[], void>({
      query: () => '/projects',
      providesTags: ['Project'],
    }),
    getProject: builder.query<Project, string>({
      query: (id) => `/projects/${id}`,
      providesTags: (_result, _error, id) => [{ type: 'Project', id }],
    }),
    getProjectWithComponents: builder.query<ProjectWithComponents, string>({
      query: (id) => `/projects/${id}/components`,
      transformResponse: (raw: BackendProjectWithComponents) => mapBackendProjectWithComponents(raw),
      providesTags: (_result, _error, id) => [{ type: 'Project', id }],
    }),
    createProject: builder.mutation<Project, CreateProjectRequest>({
      query: (project) => ({
        url: '/projects',
        method: 'POST',
        body: project,
      }),
      invalidatesTags: ['Project'],
    }),
    updateProject: builder.mutation<Project, { id: string; data: Partial<CreateProjectRequest> }>({
      query: ({ id, data }) => ({
        url: `/projects/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: 'Project', id }],
    }),
    saveProjectComponents: builder.mutation<ProjectWithComponents, SaveProjectComponentsRequest>({
      query: ({ projectId, components }) => ({
        url: `/projects/${projectId}/components`,
        method: 'PUT',
        body: { components },
      }),
      transformResponse: (raw: BackendProjectWithComponents) => mapBackendProjectWithComponents(raw),
      invalidatesTags: (_result, _error, { projectId }) => [{ type: 'Project', id: projectId }],
    }),
    deleteProject: builder.mutation<void, string>({
      query: (id) => ({
        url: `/projects/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Project'],
    }),
  }),
})

export const {
  useGetProjectsQuery,
  useGetProjectQuery,
  useGetProjectWithComponentsQuery,
  useCreateProjectMutation,
  useUpdateProjectMutation,
  useSaveProjectComponentsMutation,
  useDeleteProjectMutation,
} = projectsApi
