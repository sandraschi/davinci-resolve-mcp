import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Tools } from '@/pages/tools';
import { Actions } from '@/pages/actions';
import Logs from '@/pages/logs';
import { Chat } from '@/pages/chat';
import { Settings } from '@/pages/settings';
import { Projects } from '@/pages/projects';
import { Timeline } from '@/pages/timeline';
import { Render } from '@/pages/render';
import { Fairlight } from '@/pages/fairlight';
import { Help } from '@/pages/help';
import { Workflows } from '@/pages/workflows';

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/render" element={<Render />} />
          <Route path="/fairlight" element={<Fairlight />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/actions" element={<Actions />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
