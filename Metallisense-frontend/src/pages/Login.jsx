import { useState, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { Mail, Lock, LogIn, Cpu, Database, Activity, Zap, Shield, BarChart3, TrendingUp, Settings } from "lucide-react";
import {
  ReactFlow,
  Background,
  MarkerType,
  Handle,
  Position,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import logo from "../assets/Metallisense-logo.png";

// Custom Node Component with Handles for edge connections
const CustomNode = ({ data }) => {
  return (
    <div 
      className="px-3 py-2.5 rounded-2xl shadow-xl border-2 backdrop-blur-sm transition-all duration-200 hover:shadow-2xl cursor-grab active:cursor-grabbing relative"
      style={{
        background: data.gradient,
        borderColor: data.borderColor,
        minWidth: data.size === "large" ? "180px" : data.size === "small" ? "130px" : "155px",
      }}
    >
      {/* Connection Handles */}
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: data.borderColor, width: 10, height: 10, border: '2px solid white' }}
      />
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ background: data.borderColor, width: 10, height: 10, border: '2px solid white' }}
      />
      <Handle 
        type="target" 
        position={Position.Left} 
        id="left"
        style={{ background: data.borderColor, width: 10, height: 10, border: '2px solid white' }}
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        id="right"
        style={{ background: data.borderColor, width: 10, height: 10, border: '2px solid white' }}
      />
      
      <div className="flex items-center gap-2.5">
        <div 
          className="p-2 rounded-xl shadow-md"
          style={{ backgroundColor: data.iconBg }}
        >
          {data.icon}
        </div>
        <div>
          <div className="font-bold text-gray-800" style={{ fontSize: data.size === "large" ? "14px" : "12px" }}>{data.label}</div>
          <div className="text-gray-500" style={{ fontSize: data.size === "large" ? "11px" : "10px" }}>{data.sublabel}</div>
        </div>
      </div>
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

// Nodes positioned in a scattered, organic creative pattern - using more space
const initialNodes = [
  {
    id: "1",
    type: "custom",
    position: { x: 20, y: 10 },
    data: {
      label: "Spectrometer",
      sublabel: "Raw Data Input",
      icon: <Activity className="w-5 h-5 text-emerald-600" />,
      borderColor: "#10b981",
      iconBg: "#d1fae5",
      gradient: "linear-gradient(145deg, #ffffff 0%, #d1fae5 100%)",
      size: "large",
    },
  },
  {
    id: "2",
    type: "custom",
    position: { x: 320, y: 45 },
    data: {
      label: "AI Engine",
      sublabel: "Neural Network",
      icon: <Cpu className="w-5 h-5 text-blue-600" />,
      borderColor: "#3b82f6",
      iconBg: "#dbeafe",
      gradient: "linear-gradient(145deg, #ffffff 0%, #dbeafe 100%)",
      size: "large",
    },
  },
  {
    id: "3",
    type: "custom",
    position: { x: 180, y: 130 },
    data: {
      label: "Training DB",
      sublabel: "Historical Data",
      icon: <Database className="w-4 h-4 text-purple-600" />,
      borderColor: "#8b5cf6",
      iconBg: "#ede9fe",
      gradient: "linear-gradient(145deg, #ffffff 0%, #ede9fe 100%)",
      size: "small",
    },
  },
  {
    id: "4",
    type: "custom",
    position: { x: 450, y: 160 },
    data: {
      label: "Anomaly Detection",
      sublabel: "Real-time Analysis",
      icon: <Shield className="w-5 h-5 text-amber-600" />,
      borderColor: "#f59e0b",
      iconBg: "#fef3c7",
      gradient: "linear-gradient(145deg, #ffffff 0%, #fef3c7 100%)",
      size: "medium",
    },
  },
  {
    id: "5",
    type: "custom",
    position: { x: 35, y: 220 },
    data: {
      label: "Optimizer",
      sublabel: "Alloy Mix",
      icon: <Zap className="w-4 h-4 text-rose-600" />,
      borderColor: "#f43f5e",
      iconBg: "#ffe4e6",
      gradient: "linear-gradient(145deg, #ffffff 0%, #ffe4e6 100%)",
      size: "small",
    },
  },
  {
    id: "6",
    type: "custom",
    position: { x: 280, y: 280 },
    data: {
      label: "Analytics",
      sublabel: "Quality Insights",
      icon: <BarChart3 className="w-5 h-5 text-teal-600" />,
      borderColor: "#14b8a6",
      iconBg: "#ccfbf1",
      gradient: "linear-gradient(145deg, #ffffff 0%, #ccfbf1 100%)",
      size: "large",
    },
  },
  {
    id: "7",
    type: "custom",
    position: { x: 500, y: 320 },
    data: {
      label: "Trends",
      sublabel: "Predictions",
      icon: <TrendingUp className="w-4 h-4 text-indigo-600" />,
      borderColor: "#6366f1",
      iconBg: "#e0e7ff",
      gradient: "linear-gradient(145deg, #ffffff 0%, #e0e7ff 100%)",
      size: "small",
    },
  },
  {
    id: "8",
    type: "custom",
    position: { x: 100, y: 360 },
    data: {
      label: "Config",
      sublabel: "Settings",
      icon: <Settings className="w-4 h-4 text-gray-600" />,
      borderColor: "#6b7280",
      iconBg: "#f3f4f6",
      gradient: "linear-gradient(145deg, #ffffff 0%, #f3f4f6 100%)",
      size: "small",
    },
  },
];

// Edges with organic curved connections - bezier for natural flow
const initialEdges = [
  { 
    id: "e1-2", 
    source: "1", 
    target: "2", 
    type: "default",
    animated: true,
    style: { stroke: "#10b981", strokeWidth: 2.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981", width: 18, height: 18 },
  },
  { 
    id: "e1-3", 
    source: "1", 
    target: "3", 
    sourceHandle: "right",
    type: "default",
    animated: true,
    style: { stroke: "#8b5cf6", strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6", width: 16, height: 16 },
  },
  { 
    id: "e2-4", 
    source: "2", 
    target: "4", 
    type: "default",
    animated: true,
    style: { stroke: "#f59e0b", strokeWidth: 2.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b", width: 18, height: 18 },
  },
  { 
    id: "e3-5", 
    source: "3", 
    target: "5", 
    targetHandle: "left",
    type: "default",
    animated: true,
    style: { stroke: "#f43f5e", strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e", width: 16, height: 16 },
  },
  { 
    id: "e3-6", 
    source: "3", 
    target: "6", 
    type: "default",
    animated: true,
    style: { stroke: "#14b8a6", strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#14b8a6", width: 16, height: 16 },
  },
  { 
    id: "e4-6", 
    source: "4", 
    target: "6", 
    type: "default",
    animated: true,
    style: { stroke: "#14b8a6", strokeWidth: 2, strokeDasharray: "6,4" },
  },
  { 
    id: "e4-7", 
    source: "4", 
    target: "7", 
    type: "default",
    animated: true,
    style: { stroke: "#6366f1", strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1", width: 16, height: 16 },
  },
  { 
    id: "e5-6", 
    source: "5", 
    target: "6", 
    sourceHandle: "right",
    type: "default",
    animated: true,
    style: { stroke: "#f43f5e", strokeWidth: 2, strokeDasharray: "6,4" },
  },
  { 
    id: "e6-7", 
    source: "6", 
    target: "7", 
    sourceHandle: "right",
    type: "default",
    animated: true,
    style: { stroke: "#6366f1", strokeWidth: 2, strokeDasharray: "6,4" },
  },
  { 
    id: "e5-8", 
    source: "5", 
    target: "8", 
    type: "default",
    animated: true,
    style: { stroke: "#6b7280", strokeWidth: 1.5, strokeDasharray: "4,4" },
  },
  { 
    id: "e6-8", 
    source: "6", 
    target: "8", 
    targetHandle: "left",
    type: "default",
    animated: true,
    style: { stroke: "#6b7280", strokeWidth: 1.5, strokeDasharray: "4,4" },
  },
];

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  
  // State for draggable nodes
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    try {
      await loginWithGoogle();
      navigate("/dashboard");
    } catch (error) {
      console.error("Google login failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen w-screen overflow-auto flex items-center justify-center p-4 sm:p-6 md:p-8 relative"
      style={{
        background: "#f7fef9",
      }}
    >
      {/* Corner gradient blobs - pure green shades */}
      <div 
        className="absolute inset-0 overflow-hidden"
        style={{
          background: `
            radial-gradient(ellipse 70% 70% at 0% 0%, rgba(74, 222, 128, 0.35) 0%, transparent 70%),
            radial-gradient(ellipse 60% 60% at 100% 0%, rgba(134, 239, 172, 0.3) 0%, transparent 65%),
            radial-gradient(ellipse 65% 65% at 100% 100%, rgba(34, 197, 94, 0.25) 0%, transparent 70%),
            radial-gradient(ellipse 70% 70% at 0% 100%, rgba(74, 222, 128, 0.3) 0%, transparent 65%),
            radial-gradient(ellipse 40% 40% at 50% 50%, rgba(187, 247, 208, 0.4) 0%, transparent 60%)
          `,
        }}
      />
      
      {/* Light glossy shine overlay */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            linear-gradient(160deg, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0.2) 20%, transparent 50%),
            linear-gradient(340deg, transparent 50%, rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.35) 100%)
          `,
        }}
      />

      {/* Main Container - Flex row with Welcome Card and Login Form */}
      <div className="relative z-10 flex flex-col lg:flex-row gap-8 w-full max-w-6xl">
        
        {/* Left Side - Welcome Card with ReactFlow inside */}
        <div 
          className="hidden lg:flex flex-col flex-1 rounded-3xl shadow-2xl shadow-grey border border-white/60 overflow-hidden"
          style={{
            background: "linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(240,253,244,0.9) 100%)",
            backdropFilter: "blur(20px)",
            minHeight: "580px",
          }}
        >
          {/* Header inside the card */}
          <div className="p-6 pb-2">
            <h2 className="text-2xl font-bold text-gray-800">
              Welcome to <span className="text-emerald-600">MetalliSense</span>
            </h2>
            <p className="text-gray-500 mt-1 text-xs">
              AI-Powered Metal Analysis • Drag nodes to explore
            </p>
          </div>

          {/* ReactFlow Container inside the card */}
          <div className="flex-1 px-4 pb-4">
            <div 
              className="w-full h-full rounded-2xl overflow-hidden border border-emerald-200/50 shadow-inner"
              style={{
                background: "#ffffff",
                minHeight: "480px",
              }}
            >
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
                fitViewOptions={{ padding: 0.15 }}
                panOnDrag={true}
                zoomOnScroll={true}
                zoomOnPinch={true}
                zoomOnDoubleClick={false}
                nodesDraggable={true}
                nodesConnectable={false}
                elementsSelectable={true}
                minZoom={0.5}
                maxZoom={1.5}
                proOptions={{ hideAttribution: true }}
                defaultEdgeOptions={{
                  type: "default",
                  animated: true,
                }}
              >
                <Background color="black" gap={20} size={1} variant="dots"  />
              </ReactFlow>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-[420px] flex items-center justify-center">
          <div 
            className="w-full rounded-2xl sm:rounded-3xl shadow-2xl p-5 sm:p-8 border border-white/60"
            style={{
              background: "linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)",
              backdropFilter: "blur(20px)",
            }}
          >
          {/* Logo and Title */}
          <div className="text-center mb-4 sm:mb-6">
            <img
              src={logo}
              alt="MetalliSense Logo"
              className="h-10 sm:h-14 w-auto mx-auto mb-2 sm:mb-3"
            />
            <h1 className="text-lg sm:text-xl font-bold text-gray-800">
              Sign in to your account
            </h1>
            <p className="text-gray-500 mt-1 text-xs sm:text-sm">
              Access your metal analysis dashboard
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
            {/* Email Input */}
            <div>
              <label
                htmlFor="email"
                className="block text-xs sm:text-sm font-medium text-gray-700 mb-1"
              >
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 sm:h-5 sm:w-5 text-emerald-500" />
                </div>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="pl-9 sm:pl-10"
                  required
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label
                htmlFor="password"
                className="block text-xs sm:text-sm font-medium text-gray-700 mb-1"
              >
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 sm:h-5 sm:w-5 text-emerald-500" />
                </div>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="pl-9 sm:pl-10"
                  required
                />
              </div>
            </div>

            {/* Forgot Password Link */}
            <div className="flex items-center justify-end">
              <Link
                to="/forgot-password"
                className="text-xs sm:text-sm text-emerald-600 hover:text-emerald-700 font-medium"
              >
                Forgot password?
              </Link>
            </div>

            {/* Login Button */}
            <Button
              type="submit"
              variant="primary"
              className="w-full flex items-center justify-center space-x-2 py-2.5 sm:py-3"
              disabled={isLoading}
            >
              {isLoading ? (
                <span>Signing in...</span>
              ) : (
                <>
                  <LogIn className="h-4 w-4 sm:h-5 sm:w-5" />
                  <span>Sign In</span>
                </>
              )}
            </Button>
          </form>

          {/* Divider */}
          <div className="my-4 sm:my-5">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-xs sm:text-sm">
                <span className="px-3 bg-white text-gray-500 rounded">
                  Or continue with
                </span>
              </div>
            </div>
          </div>

          {/* Google Sign In Button */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={isLoading}
            className="w-full flex items-center justify-center px-4 py-2.5 sm:py-3 border border-gray-200 rounded-xl shadow-sm text-xs sm:text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <svg className="w-4 h-4 sm:w-5 sm:h-5 mr-2" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google
          </button>

          {/* Sign Up Link */}
          <div className="mt-4 sm:mt-5 text-center">
            <p className="text-xs sm:text-sm text-gray-600">
              Don't have an account?{" "}
              <Link
                to="/signup"
                className="font-semibold text-emerald-600 hover:text-emerald-700"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
      
      </div>
    </div>
  );
}
