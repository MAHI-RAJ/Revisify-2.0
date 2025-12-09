import { useEffect } from 'react';
import { useDashboardStore } from '@/state/dashboardStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader } from '@/components/Loader';
import { FileText, Clock, Target, Flame, TrendingUp, AlertTriangle } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { format } from 'date-fns';

const COLORS = ['hsl(262, 83%, 58%)', 'hsl(199, 89%, 48%)', 'hsl(142, 76%, 36%)', 'hsl(38, 92%, 50%)', 'hsl(0, 84%, 60%)'];

export default function Dashboard() {
  const { stats, studyTimeData, accuracyData, topicPerformance, weakTopics, completionData, fetchAllDashboardData, isLoading, error } = useDashboardStore();

  useEffect(() => {
    fetchAllDashboardData();
  }, [fetchAllDashboardData]);

  if (isLoading) return <div className="flex justify-center py-20"><Loader size="lg" text="Loading dashboard..." /></div>;
  if (error) return <div className="container mx-auto px-4 py-8 text-center text-destructive">{error}</div>;

  const statCards = [
    { label: 'Documents', value: stats?.totalDocuments || 0, icon: FileText, color: 'text-primary' },
    { label: 'Study Time', value: `${Math.round((stats?.totalStudyTime || 0) / 60)}h`, icon: Clock, color: 'text-info' },
    { label: 'Avg Score', value: `${stats?.averageScore || 0}%`, icon: Target, color: 'text-success' },
    { label: 'Streak', value: `${stats?.streakDays || 0} days`, icon: Flame, color: 'text-warning' },
  ];

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((s) => (
          <Card key={s.label} className="animate-fade-in">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{s.label}</p>
                  <p className="text-3xl font-bold mt-1">{s.value}</p>
                </div>
                <div className={`h-12 w-12 rounded-xl bg-muted flex items-center justify-center ${s.color}`}>
                  <s.icon className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Study Time Chart */}
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="h-5 w-5" />Study Time</CardTitle><CardDescription>Minutes spent learning per day</CardDescription></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={studyTimeData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="date" tickFormatter={(v) => format(new Date(v), 'MMM d')} className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                <Line type="monotone" dataKey="minutes" stroke="hsl(262, 83%, 58%)" strokeWidth={2} dot={{ fill: 'hsl(262, 83%, 58%)' }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Accuracy Chart */}
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Target className="h-5 w-5" />Accuracy</CardTitle><CardDescription>Quiz performance over time</CardDescription></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={accuracyData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="date" tickFormatter={(v) => format(new Date(v), 'MMM d')} className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                <Bar dataKey="accuracy" fill="hsl(142, 76%, 36%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Completion Pie */}
        <Card>
          <CardHeader><CardTitle>Completion</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={completionData} dataKey="value" nameKey="label" cx="50%" cy="50%" outerRadius={80} label>
                  {completionData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Topic Performance */}
        <Card>
          <CardHeader><CardTitle>Topic Performance</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topicPerformance.slice(0, 5).map((t) => (
                <div key={t.topic} className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1"><span>{t.topic}</span><span className="font-medium">{t.accuracy}%</span></div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden"><div className="h-full gradient-primary rounded-full" style={{ width: `${t.accuracy}%` }} /></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Weak Topics */}
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-warning" />Areas to Improve</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {weakTopics.map((t) => (
                <div key={t.topic} className="p-3 rounded-lg bg-warning/10 border border-warning/20">
                  <p className="font-medium text-sm">{t.topic}</p>
                  <p className="text-xs text-muted-foreground mt-1">Accuracy: {t.accuracy}%</p>
                </div>
              ))}
              {weakTopics.length === 0 && <p className="text-muted-foreground text-sm">No weak areas detected</p>}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
