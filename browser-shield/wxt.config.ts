import { defineConfig } from 'wxt';

export default defineConfig({
  manifest: {
    name: 'CyberOS Browser Shield',
    description: 'Real-time web protection connected to CyberOS Intelligence Fabric',
    version: '1.0.0',
    permissions: ['tabs', 'storage', 'activeTab'],
    host_permissions: ['http://localhost:8000/*'],
  },
  vite: () => ({
    build: {
      target: 'esnext'
    }
  })
});
