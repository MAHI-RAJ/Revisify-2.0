import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart
} from 'recharts';

// Stat Card Widget
interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: number;
  color?: string;
}

export function StatCard({ label, value, icon: Icon, trend, color = 'text-primary' }: StatCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend > 0) return <TrendingUp className="h-4 w-4 text-success" />;
    if (trend < 0) return <TrendingDown className="h-4 w-4 text-destructive" />;
    return <Minus className="h-4 w-4 text-muted-foreground" />;
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="text-3xl font-bold mt-1">{value}</p>
              {trend !== undefined && (
                <div className="flex items-center gap-1 mt-2">
                  {getTrendIcon()}
                  <span className={cn(
                    'text-xs font-medium',
                    trend > 0 ? 'text-success' : trend < 0 ? 'text-destructive' : 'text-muted-foreground'
                  )}>
                    {trend > 0 ? '+' : ''}{trend}% from last week
                  </span>
                </div>
              )}
            </div>
            <div className={cn('h-14 w-14 rounded-2xl bg-muted flex items-center justify-center', color)}>
              <Icon className="h-7 w-7" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// Progress Card Widget
interface ProgressCardProps {
  title: string;
  description?: string;
  items: { label: string; value: number; max?: number }[];
}

export function ProgressCard({ title, description, items }: ProgressCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-4">
        {items.map((item, index) => (
          <div key={index}>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-muted-foreground">{item.label}</span>
              <span className="font-medium">{item.value}%</span>
            </div>
            <Progress value={item.value} className="h-2" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// Line Chart Widget
interface LineChartWidgetProps {
  title: string;
  description?: string;
  data: any[];
  dataKey: string;
  xAxisKey: string;
  color?: string;
  formatXAxis?: (value: string) => string;
}

export function LineChartWidget({ 
  title, description, data, dataKey, xAxisKey, color = 'hsl(262, 83%, 58%)', formatXAxis 
}: LineChartWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey={xAxisKey} 
              tickFormatter={formatXAxis} 
              className="text-xs"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis className="text-xs" tick={{ fill: 'hsl(var(--muted-foreground))' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))', 
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px'
              }} 
            />
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={2} 
              dot={{ fill: color, r: 4 }}
              activeDot={{ r: 6, fill: color }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// Area Chart Widget
interface AreaChartWidgetProps {
  title: string;
  description?: string;
  data: any[];
  dataKey: string;
  xAxisKey: string;
  color?: string;
  formatXAxis?: (value: string) => string;
}

export function AreaChartWidget({ 
  title, description, data, dataKey, xAxisKey, color = 'hsl(262, 83%, 58%)', formatXAxis 
}: AreaChartWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey={xAxisKey} 
              tickFormatter={formatXAxis}
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis tick={{ fill: 'hsl(var(--muted-foreground))' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))', 
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px'
              }} 
            />
            <Area 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              fill="url(#colorGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// Bar Chart Widget
interface BarChartWidgetProps {
  title: string;
  description?: string;
  data: any[];
  dataKey: string;
  xAxisKey: string;
  color?: string;
  formatXAxis?: (value: string) => string;
}

export function BarChartWidget({ 
  title, description, data, dataKey, xAxisKey, color = 'hsl(142, 76%, 36%)', formatXAxis 
}: BarChartWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey={xAxisKey} 
              tickFormatter={formatXAxis}
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis tick={{ fill: 'hsl(var(--muted-foreground))' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))', 
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px'
              }} 
            />
            <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// Pie Chart Widget
interface PieChartWidgetProps {
  title: string;
  description?: string;
  data: { label: string; value: number }[];
  colors?: string[];
}

const DEFAULT_COLORS = [
  'hsl(262, 83%, 58%)',
  'hsl(199, 89%, 48%)',
  'hsl(142, 76%, 36%)',
  'hsl(38, 92%, 50%)',
  'hsl(0, 84%, 60%)',
];

export function PieChartWidget({ title, description, data, colors = DEFAULT_COLORS }: PieChartWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="label"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ label, percent }) => `${label} ${(percent * 100).toFixed(0)}%`}
              labelLine={false}
            >
              {data.map((_, index) => (
                <Cell key={index} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))', 
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px'
              }} 
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
