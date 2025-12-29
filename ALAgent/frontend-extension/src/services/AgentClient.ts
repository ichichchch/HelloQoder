import axios, { AxiosInstance } from 'axios';
import { AgentRequest, AgentResponse, RagQueryRequest, RagQueryResponse } from '../core/types';

export class AgentClient {
  private _agentApi: AxiosInstance;
  private _ragApi: AxiosInstance;

  constructor(agentApiUrl: string, ragApiUrl: string) {
    this._agentApi = axios.create({
      baseURL: agentApiUrl,
      timeout: 120000, // 2 minutes timeout for LLM calls
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this._ragApi = axios.create({
      baseURL: ragApiUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  public updateConfig(agentApiUrl: string, ragApiUrl: string) {
    this._agentApi.defaults.baseURL = agentApiUrl;
    this._ragApi.defaults.baseURL = ragApiUrl;
  }

  public async chat(request: AgentRequest): Promise<AgentResponse> {
    const response = await this._agentApi.post<AgentResponse>('/api/chat', request);
    return response.data;
  }

  public async queryContext(request: RagQueryRequest): Promise<RagQueryResponse> {
    const response = await this._ragApi.post<RagQueryResponse>('/api/query', request);
    return response.data;
  }

  public async healthCheck(): Promise<{ agent: boolean; rag: boolean }> {
    const results = { agent: false, rag: false };

    try {
      await this._agentApi.get('/health');
      results.agent = true;
    } catch {
      // Agent API not available
    }

    try {
      await this._ragApi.get('/health');
      results.rag = true;
    } catch {
      // RAG API not available
    }

    return results;
  }
}
