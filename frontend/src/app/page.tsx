'use client';

import React, { useState, useEffect } from 'react';
import {
  Wrench,
  AlertTriangle,
  Calendar,
  Layers,
  ShieldCheck,
  Activity,
  CloudRain,
  Clock,
  CheckCircle2,
  XCircle,
  PlusCircle,
  RefreshCw,
  Sparkles,
  ArrowRight,
  Car,
  DollarSign,
  Send,
  FileText,
  UserCheck,
  ChevronRight,
  AlertCircle,
  Mail,
  User,
  KeyRound,
  Inbox,
  LogOut,
  Gauge
} from 'lucide-react';
import { api } from '@/lib/api';

export default function PitStopDashboard() {
  // App Mode Switcher: Workshop Operations vs. Customer Vehicle Owner Portal
  const [appMode, setAppMode] = useState<'workshop' | 'customerPortal'>('workshop');

  const [activeTab, setActiveTab] = useState<'intake' | 'workOrders' | 'scheduling' | 'inventory' | 'weather' | 'audit'>('intake');
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Email Notifications Outbox Modal
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState<any[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<any>(null);

  // Customer Portal State
  const [loginEmail, setLoginEmail] = useState('alex.mercer@example.com');
  const [loginCode, setLoginCode] = useState('');
  const [codeSent, setCodeSent] = useState(false);
  const [customerSession, setCustomerSession] = useState<any>(null);
  const [customerGarage, setCustomerGarage] = useState<any>(null);

  // Intake Tab State
  const [intakeMessage, setIntakeMessage] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [vehicleMake, setVehicleMake] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');
  const [vehicleYear, setVehicleYear] = useState<string>('');
  const [aiExtraction, setAiExtraction] = useState<any>(null);
  const [activeRequestId, setActiveRequestId] = useState<number | null>(null);
  const [clarificationInput, setClarificationInput] = useState('');
  const [activeRequestDetail, setActiveRequestDetail] = useState<any>(null);

  // Work Orders Tab State
  const [workOrders, setWorkOrders] = useState<any[]>([]);
  const [selectedWorkOrder, setSelectedWorkOrder] = useState<any>(null);
  const [woStatusFilter, setWoStatusFilter] = useState<string>('all');
  const [mechanicNotes, setMechanicNotes] = useState('');

  // Scheduling Tab State
  const [selectedServiceType, setSelectedServiceType] = useState('brake_service');
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [availableSlots, setAvailableSlots] = useState<any[]>([]);
  const [scheduledAppointments, setScheduledAppointments] = useState<any[]>([]);
  const [bookingWoId, setBookingWoId] = useState<number | null>(null);

  // Inventory Tab State
  const [parts, setParts] = useState<any[]>([]);
  const [movements, setMovements] = useState<any[]>([]);
  const [restockPartId, setRestockPartId] = useState<number | null>(null);
  const [restockQty, setRestockQty] = useState<number>(5);

  // Weather & Audit Tab State
  const [weatherData, setWeatherData] = useState<any>(null);
  const [auditEvents, setAuditEvents] = useState<any[]>([]);
  const [automationJobs, setAutomationJobs] = useState<any[]>([]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4500);
  };

  // Initial Data Fetch
  const loadInitialData = async () => {
    try {
      const [h, a, p, wo, apps, w, notifs] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getAnalyticsSummary().catch(() => null),
        api.getParts().catch(() => []),
        api.listWorkOrders().catch(() => []),
        api.listAppointments().catch(() => []),
        api.getWeather().catch(() => null),
        api.getEmailInbox().catch(() => []),
      ]);
      setSystemHealth(h);
      setAnalytics(a);
      setParts(p);
      setWorkOrders(wo);
      setScheduledAppointments(apps);
      setWeatherData(w);
      setEmailNotifications(notifs);
      if (wo.length > 0) {
        setBookingWoId(wo[0].id);
      }
    } catch (err: any) {
      console.error('Initialization error:', err);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Poll analytics and notifications periodically
  useEffect(() => {
    const timer = setInterval(() => {
      api.getAnalyticsSummary().then(setAnalytics).catch(() => {});
      api.getEmailInbox().then(setEmailNotifications).catch(() => {});
    }, 12000);
    return () => clearInterval(timer);
  }, []);

  // Preset demo scenarios
  const applyPreset = (preset: 'brake_emergency' | 'oil_maintenance' | 'check_engine' | 'ceramic_coating') => {
    if (preset === 'brake_emergency') {
      setCustomerName('Alex Mercer');
      setCustomerPhone('415-555-0199');
      setCustomerEmail('alex.mercer@example.com');
      setVehicleMake('Toyota');
      setVehicleModel('Camry');
      setVehicleYear('2021');
      setIntakeMessage('My 2021 Toyota Camry has a severe grinding noise when applying the brakes and the pedal felt unusually spongy on the highway today. Can I drop it off tomorrow morning?');
    } else if (preset === 'oil_maintenance') {
      setCustomerName('David Kim');
      setCustomerPhone('415-555-0144');
      setCustomerEmail('david.kim@example.com');
      setVehicleMake('Subaru');
      setVehicleModel('Outback');
      setVehicleYear('2022');
      setIntakeMessage('Need a routine 30k mile full synthetic oil change and tire rotation for my Subaru Outback before a road trip next weekend.');
    } else if (preset === 'check_engine') {
      setCustomerName('Elena Rossi');
      setCustomerPhone('415-555-0811');
      setCustomerEmail('elena.rossi@example.com');
      setVehicleMake('BMW');
      setVehicleModel('330i');
      setVehicleYear('2019');
      setIntakeMessage('Check Engine Light came on this morning and the car idles roughly at stoplights with hesitation on acceleration.');
    } else if (preset === 'ceramic_coating') {
      setCustomerName('Jordan Taylor');
      setCustomerPhone('415-555-0922');
      setCustomerEmail('jordan.taylor@example.com');
      setVehicleMake('Tesla');
      setVehicleModel('Model 3');
      setVehicleYear('2023');
      setIntakeMessage('Looking to get a complete exterior hand wash, clay bar, and full 9H ceramic shield coating application.');
    }
  };

  // AI Intake Analysis
  const handleAnalyzeIntake = async () => {
    if (!intakeMessage.trim()) {
      showToast('Please type a message or select a demo preset.');
      return;
    }
    setLoading(true);
    try {
      const result = await api.analyzeIntake({
        message: intakeMessage,
        customer_name: customerName || undefined,
        customer_phone: customerPhone || undefined,
        vehicle_make: vehicleMake || undefined,
        vehicle_model: vehicleModel || undefined,
        vehicle_year: vehicleYear ? parseInt(vehicleYear) : undefined,
      });
      setAiExtraction(result);
      showToast('AI Agent successfully extracted structured service parameters!');
    } catch (err: any) {
      showToast(`AI extraction failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Save Service Request
  const handleSaveRequest = async () => {
    setLoading(true);
    try {
      const created = await api.createServiceRequest({
        workshop_id: 1,
        original_message: intakeMessage,
        customer_name: customerName,
        customer_phone: customerPhone,
        customer_email: customerEmail,
        vehicle_make: vehicleMake || aiExtraction?.vehicle_make,
        vehicle_model: vehicleModel || aiExtraction?.vehicle_model,
        vehicle_year: vehicleYear ? parseInt(vehicleYear) : aiExtraction?.vehicle_year,
      });
      setActiveRequestId(created.id);
      const detail = await api.getServiceRequestDetail(created.id);
      setActiveRequestDetail(detail);
      showToast(`Service Request #${created.id} saved! Confirmation email sent to ${customerEmail || 'customer'}.`);
      api.getAnalyticsSummary().then(setAnalytics);
      api.getEmailInbox().then(setEmailNotifications);
    } catch (err: any) {
      showToast(`Error saving request: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Submit Clarification Answer
  const handleClarificationAnswer = async () => {
    if (!activeRequestId || !clarificationInput.trim()) return;
    setLoading(true);
    try {
      await api.submitClarification(activeRequestId, clarificationInput);
      setClarificationInput('');
      const detail = await api.getServiceRequestDetail(activeRequestId);
      setActiveRequestDetail(detail);
      showToast('Clarification response logged. Request moved to Under Review.');
    } catch (err: any) {
      showToast(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Convert to Work Order
  const handleConvertToWorkOrder = async () => {
    if (!activeRequestId) return;
    setLoading(true);
    try {
      const wo = await api.createWorkOrder({
        workshop_id: 1,
        request_id: activeRequestId,
        service_type: aiExtraction?.proposed_service_type || 'general_inspection',
        estimated_duration_minutes: aiExtraction?.estimated_duration_minutes || 60,
        customer_complaint: intakeMessage,
      });
      showToast(`Created Work Order #${wo.id}!`);
      const updatedList = await api.listWorkOrders();
      setWorkOrders(updatedList);
      setBookingWoId(wo.id);
      setActiveTab('workOrders');
      handleSelectWorkOrder(wo.id);
    } catch (err: any) {
      showToast(`Error creating work order: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Work Orders & Estimate
  const handleSelectWorkOrder = async (id: number) => {
    setLoading(true);
    try {
      const detail = await api.getWorkOrderDetail(id);
      setSelectedWorkOrder(detail);
      setMechanicNotes(detail.mechanic_notes || '');
    } catch (err: any) {
      showToast(`Error loading work order detail: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateEstimate = async (woId: number) => {
    setLoading(true);
    try {
      const est = await api.createEstimate({ work_order_id: woId });
      showToast(`Draft Estimate created: $${est.grand_total.toFixed(2)}. Approval email dispatched to vehicle owner!`);
      handleSelectWorkOrder(woId);
      api.getAnalyticsSummary().then(setAnalytics);
      api.getEmailInbox().then(setEmailNotifications);
    } catch (err: any) {
      showToast(`Error generating estimate: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveEstimate = async (estId: number, woId: number) => {
    setLoading(true);
    try {
      await api.approveEstimate(estId, 'Dave Miller (Service Advisor)', 'Approved by customer under policy');
      showToast('Estimate authorized under workshop policy (Human-in-the-Loop confirmed)!');
      handleSelectWorkOrder(woId);
      api.getAnalyticsSummary().then(setAnalytics);
      api.getEmailInbox().then(setEmailNotifications);
    } catch (err: any) {
      showToast(`Error approving estimate: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateWorkOrderStatus = async (woId: number, newStatus: string) => {
    setLoading(true);
    try {
      await api.updateWorkOrder(woId, { status: newStatus, mechanic_notes: mechanicNotes });
      showToast(`Work Order #${woId} moved to ${newStatus.replace('_', ' ').toUpperCase()}`);
      handleSelectWorkOrder(woId);
      const list = await api.listWorkOrders();
      setWorkOrders(list);
      api.getAnalyticsSummary().then(setAnalytics);
      api.getEmailInbox().then(setEmailNotifications);
    } catch (err: any) {
      showToast(`Error updating status: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Scheduling Slots Search
  const handleSearchSlots = async () => {
    setLoading(true);
    try {
      const slots = await api.getAvailability(selectedServiceType, selectedDate, 90);
      setAvailableSlots(slots);
      if (slots.length > 0) {
        showToast(`Found ${slots.filter(s => s.available).length} feasible capacity slots for ${selectedDate}`);
      }
    } catch (err: any) {
      showToast(`Scheduling lookup error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Confirm Appointment
  const handleConfirmAppointment = async (slot: any) => {
    const targetWoId = bookingWoId || workOrders[0]?.id;
    if (!targetWoId) {
      showToast('Please select a Target Work Order from the dropdown before confirming a slot.');
      return;
    }
    setLoading(true);
    try {
      const idempotencyKey = `pitstop_key_${targetWoId}_${Date.now()}`;
      const app = await api.confirmAppointment({
        work_order_id: targetWoId,
        bay_id: slot.bay_id,
        mechanic_id: slot.mechanic_id,
        start_at: slot.start_at,
        idempotency_key: idempotencyKey,
      });
      showToast(`Appointment #${app.id} confirmed for Work Order #${targetWoId}! Synced with Google Calendar & email dispatched.`);
      const apps = await api.listAppointments();
      setScheduledAppointments(apps);
      handleSearchSlots();
      api.getAnalyticsSummary().then(setAnalytics);
      api.getEmailInbox().then(setEmailNotifications);
    } catch (err: any) {
      showToast(`Booking failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Calendar Sync Simulation & Injected Failure / Recovery
  const handleCalendarSyncTest = async (appId: number, simulateFailure: boolean) => {
    setLoading(true);
    try {
      const res = await api.syncCalendar(appId, simulateFailure);
      if (res.success) {
        showToast('Calendar synchronization SUCCESSFUL. Event synced with external calendar.');
      } else {
        showToast(`Failure scenario demonstrated: ${res.message}`);
      }
      const apps = await api.listAppointments();
      setScheduledAppointments(apps);
    } catch (err: any) {
      showToast(`Sync error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Inventory Restock
  const handleRestockPart = async () => {
    if (!restockPartId) return;
    setLoading(true);
    try {
      await api.recordMovement({
        part_id: restockPartId,
        quantity_delta: restockQty,
        reason: 'Authorized restock delivery from distributor',
      });
      showToast(`Successfully added ${restockQty} units to inventory!`);
      const updatedParts = await api.getParts();
      setParts(updatedParts);
      api.getAnalyticsSummary().then(setAnalytics);
    } catch (err: any) {
      showToast(`Restock error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Proactive Automation Cycle Trigger
  const handleRunAutomation = async () => {
    setLoading(true);
    try {
      const res = await api.runAutomation();
      const r = res.results || {};
      const parts = [];
      if (r.reminders_prepared) parts.push(`${r.reminders_prepared} reminders`);
      if (r.overdue_jobs_flagged) parts.push(`${r.overdue_jobs_flagged} overdue flagged`);
      if (r.low_stock_alerts) parts.push(`${r.low_stock_alerts} stock alerts`);
      if (r.retries_processed) parts.push(`${r.retries_processed} retries`);
      const summaryText = parts.length > 0 ? parts.join(', ') : 'All background operations verified (no pending alerts)';
      showToast(`Automation cycle completed: ${summaryText}`);
      const jobs = await api.listAutomationJobs();
      setAutomationJobs(jobs);
      api.getAnalyticsSummary().then(setAnalytics);
    } catch (err: any) {
      showToast(`Automation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Customer Portal Handlers
  const handleSendCustomerCode = async () => {
    if (!loginEmail || !loginEmail.includes('@')) {
      showToast('Please enter a valid email address.');
      return;
    }
    setLoading(true);
    try {
      const res = await api.sendAuthCode(loginEmail);
      setCodeSent(true);
      showToast(`Verification code sent! Hint: check Email Outbox or use code: ${res.code_preview}`);
      if (res.code_preview) {
        setLoginCode(res.code_preview);
      }
      api.getEmailInbox().then(setEmailNotifications);
    } catch (err: any) {
      showToast(`Auth error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCustomerCode = async () => {
    if (!loginCode) {
      showToast('Please enter the 6-digit verification code.');
      return;
    }
    setLoading(true);
    try {
      const res = await api.verifyAuthCode(loginEmail, loginCode);
      setCustomerSession(res.customer);
      showToast(`Welcome back to your Garage, ${res.customer.name}!`);
      loadCustomerGarageData(res.customer.email);
    } catch (err: any) {
      showToast(`Verification failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadCustomerGarageData = async (email: string) => {
    try {
      const garage = await api.getCustomerGarage(email);
      setCustomerGarage(garage);
    } catch (err: any) {
      console.error('Failed to load garage:', err);
    }
  };

  const handleCustomerApproveEstimate = async (estimateId: number) => {
    setLoading(true);
    try {
      await api.customerApproveEstimate(estimateId, customerSession?.name);
      showToast('Estimate authorized! Our certified mechanics have received confirmation.');
      if (customerSession?.email) {
        loadCustomerGarageData(customerSession.email);
      }
      loadInitialData();
    } catch (err: any) {
      showToast(`Approval error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Load Audit Trail
  const handleLoadAudit = async () => {
    setLoading(true);
    try {
      const events = await api.getAuditEvents(50);
      setAuditEvents(events);
      const jobs = await api.listAutomationJobs();
      setAutomationJobs(jobs);
    } catch (err: any) {
      showToast(`Error fetching audit events: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'audit') {
      handleLoadAudit();
    } else if (activeTab === 'scheduling') {
      handleSearchSlots();
    }
  }, [activeTab]);

  return (
    <div className="flex-1 flex flex-col bg-[#070b14] text-slate-100 min-h-screen">
      {/* Toast Alert Banner */}
      {toastMessage && (
        <div className="fixed top-5 right-5 z-50 bg-gradient-to-r from-orange-600 to-amber-600 text-white px-5 py-3 rounded-xl shadow-2xl flex items-center space-x-3 border border-orange-400/30 animate-in fade-in slide-in-from-top-4 duration-200">
          <Sparkles className="w-5 h-5 text-yellow-200 animate-spin" />
          <span className="text-sm font-semibold">{toastMessage}</span>
        </div>
      )}

      {/* Top Header Bar */}
      <header className="border-b border-slate-800 bg-[#0c1222]/90 backdrop-blur-md sticky top-0 z-40 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-orange-500/30 border border-orange-400/40">
              <Wrench className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-black text-xl tracking-tight racing-gradient-text">PitStop AI</span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/30">
                  Apex Ops v2.0
                </span>
              </div>
              <p className="text-xs text-slate-400">Intelligent Automotive Workshop & Vehicle Owner Platform</p>
            </div>
          </div>

          {/* Central Role / Mode Switcher */}
          <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-slate-800 shadow-inner">
            <button
              onClick={() => setAppMode('workshop')}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                appMode === 'workshop'
                  ? 'bg-gradient-to-r from-orange-500 to-amber-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Wrench className="w-3.5 h-3.5" />
              <span>Workshop Staff Hub</span>
            </button>
            <button
              onClick={() => {
                setAppMode('customerPortal');
                if (customerSession?.email) {
                  loadCustomerGarageData(customerSession.email);
                }
              }}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                appMode === 'customerPortal'
                  ? 'bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Car className="w-3.5 h-3.5" />
              <span>Vehicle Owner Garage</span>
            </button>
          </div>

          {/* Actions & Live Email Outbox Drawer Trigger */}
          <div className="flex items-center space-x-3 text-xs">
            <button
              onClick={() => {
                api.getEmailInbox().then(setEmailNotifications);
                setShowEmailModal(true);
              }}
              className="relative px-3 py-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-sky-400 font-semibold border border-sky-500/30 flex items-center space-x-1.5 transition-colors shadow-sm"
            >
              <Mail className="w-3.5 h-3.5 text-sky-400" />
              <span>Email Outbox</span>
              {emailNotifications.length > 0 && (
                <span className="w-5 h-5 rounded-full bg-sky-500 text-slate-950 font-bold text-[10px] flex items-center justify-center ml-1">
                  {emailNotifications.length}
                </span>
              )}
            </button>

            <button
              onClick={() => {
                api.seedDatabase().then(() => {
                  showToast('PitStop AI workshop database reseeded with demonstration data!');
                  loadInitialData();
                });
              }}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium border border-slate-700 flex items-center space-x-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reseed Demo</span>
            </button>
          </div>
        </div>
      </header>

      {/* ========================================================================= */}
      {/* VEHICLE OWNER PORTAL MODE ("MY PITSTOP GARAGE")                           */}
      {/* ========================================================================= */}
      {appMode === 'customerPortal' ? (
        <main className="flex-1 max-w-7xl mx-auto w-full p-6 space-y-6">
          {!customerSession ? (
            /* Email Sign-In with OTP Card */
            <div className="max-w-md mx-auto my-12 glass-panel p-8 rounded-3xl border border-sky-500/30 shadow-2xl space-y-5">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-2xl bg-sky-500/10 border border-sky-500/30 text-sky-400 flex items-center justify-center mx-auto">
                  <KeyRound className="w-6 h-6" />
                </div>
                <h2 className="text-xl font-bold text-slate-100">Sign In to My PitStop Garage</h2>
                <p className="text-xs text-slate-400">
                  Passwordless email authentication. Enter your email to receive a secure single-use access code.
                </p>
              </div>

              {/* Demo Quick-Fill Buttons */}
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">SRS Demo Owner:</span>
                  <button
                    onClick={() => setLoginEmail('alex.mercer@example.com')}
                    className="text-orange-400 hover:text-orange-300 font-semibold underline"
                  >
                    alex.mercer@example.com
                  </button>
                </div>
                <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800">
                  <span className="text-emerald-400 font-medium">Real Gmail Inbox:</span>
                  <button
                    onClick={() => setLoginEmail('hiramen17@gmail.com')}
                    className="text-emerald-400 hover:text-emerald-300 font-semibold underline"
                  >
                    hiramen17@gmail.com
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Your Email Address</label>
                  <input
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-sky-500"
                  />
                </div>

                {!codeSent ? (
                  <button
                    onClick={handleSendCustomerCode}
                    disabled={loading}
                    className="w-full py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 text-white font-semibold text-sm shadow-lg shadow-sky-500/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
                  >
                    <Mail className="w-4 h-4" />
                    <span>Send Verification Code</span>
                  </button>
                ) : (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <div>
                      <label className="text-xs text-sky-400 block mb-1 font-semibold">Enter 6-Digit Code (Sent to Email)</label>
                      <input
                        type="text"
                        maxLength={6}
                        value={loginCode}
                        onChange={(e) => setLoginCode(e.target.value)}
                        placeholder="e.g. 542918"
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-sky-500 text-sky-300 font-mono text-center tracking-widest text-lg focus:outline-none"
                      />
                    </div>
                    <button
                      onClick={handleVerifyCustomerCode}
                      disabled={loading}
                      className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 text-white font-semibold text-sm shadow-lg shadow-emerald-500/20 flex items-center justify-center space-x-2 transition-all"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Verify & Enter Garage</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            /* Authenticated Customer Garage View */
            <div className="space-y-6">
              {/* Profile Bar */}
              <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-2xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
                    <User className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
                      <span>{customerSession.name}&apos;s Garage</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        Verified Vehicle Owner
                      </span>
                    </h2>
                    <p className="text-xs text-slate-400">{customerSession.email} | Notifications Active</p>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setCustomerSession(null);
                    setCustomerGarage(null);
                    setCodeSent(false);
                    setLoginCode('');
                    showToast('Logged out of Customer Garage.');
                  }}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center space-x-1.5 transition-colors"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>

              {/* Registered Vehicles */}
              <div>
                <h3 className="font-bold text-sm text-slate-200 mb-3 flex items-center space-x-2">
                  <Car className="w-4 h-4 text-sky-400" />
                  <span>My Registered Vehicles & Health Intervals</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {customerGarage?.vehicles?.map((veh: any) => (
                    <div key={veh.id} className="glass-panel p-4 rounded-xl border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-sm text-slate-200">{veh.year} {veh.make} {veh.model}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                          {veh.license_plate || 'PLATE-N/A'}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                        <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                          <span className="text-[10px] text-slate-400 block">Odometer</span>
                          <span className="font-mono font-bold text-slate-200">{veh.mileage?.toLocaleString()} mi</span>
                        </div>
                        <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                          <span className="text-[10px] text-slate-400 block">Next Inspection</span>
                          <span className="font-mono font-bold text-sky-400">{veh.next_service_mileage?.toLocaleString()} mi</span>
                        </div>
                      </div>

                      <div className="text-[11px] text-slate-400 flex items-center space-x-1.5">
                        <Gauge className="w-3.5 h-3.5 text-orange-400" />
                        <span>Recommended: 5,000-mile synthetic oil & brake inspection</span>
                      </div>
                    </div>
                  ))}
                  {(!customerGarage?.vehicles || customerGarage.vehicles.length === 0) && (
                    <div className="col-span-3 text-center py-6 text-xs text-slate-500">No vehicles registered yet.</div>
                  )}
                </div>
              </div>

              {/* Active Repairs & Live Visual Stage Tracker */}
              <div className="space-y-4">
                <h3 className="font-bold text-sm text-slate-200 flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-orange-400" />
                  <span>Live Vehicle Service & Repair Tracker</span>
                </h3>

                {customerGarage?.active_repairs?.map((repair: any) => (
                  <div key={repair.id} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs text-orange-400 font-bold uppercase tracking-wider block">
                          Work Order #{repair.id}
                        </span>
                        <h4 className="text-base font-bold text-slate-100">
                          {repair.service_type?.replace(/_/g, ' ').toUpperCase()}
                        </h4>
                      </div>
                      <span className="text-xs px-3 py-1 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 capitalize">
                        Status: {repair.status?.replace(/_/g, ' ')}
                      </span>
                    </div>

                    {/* 5-Stage Visual Progress Stepper */}
                    <div className="grid grid-cols-5 gap-2 text-center text-xs pt-2">
                      {[
                        { num: 1, title: 'Intake Logged' },
                        { num: 2, title: 'Bay Inspection' },
                        { num: 3, title: 'Estimate Ready' },
                        { num: 4, title: 'In Repair' },
                        { num: 5, title: 'Ready for Pickup' },
                      ].map((st) => {
                        const isDone = repair.current_stage >= st.num;
                        const isCurrent = repair.current_stage === st.num;
                        return (
                          <div key={st.num} className="space-y-1.5">
                            <div className={`h-2 rounded-full transition-all ${
                              isDone ? 'bg-gradient-to-r from-orange-500 to-emerald-500' : 'bg-slate-800'
                            }`} />
                            <span className={`text-[11px] block font-semibold ${
                              isCurrent ? 'text-orange-400 font-bold' : isDone ? 'text-slate-300' : 'text-slate-500'
                            }`}>
                              {st.title}
                            </span>
                          </div>
                        );
                      })}
                    </div>

                    {/* Appointment & Technician Info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
                      <div>
                        <span className="text-slate-400 block mb-0.5">Assigned Certified Mechanic</span>
                        <span className="font-semibold text-slate-200">{repair.assigned_technician}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block mb-0.5">Scheduled Bay Time</span>
                        <span className="font-semibold text-slate-200">
                          {repair.appointment ? `${new Date(repair.appointment.start_at).toLocaleDateString()} ${new Date(repair.appointment.start_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} in ${repair.appointment.bay_name}` : 'Awaiting slot confirmation'}
                        </span>
                      </div>
                    </div>

                    {/* Digital Customer Estimate Authorization Card */}
                    {repair.estimate && (
                      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm text-slate-200 flex items-center space-x-1.5">
                            <DollarSign className="w-4 h-4 text-emerald-400" />
                            <span>Formal Quote & Parts Breakdown</span>
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                            repair.estimate.status === 'approved'
                              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          }`}>
                            {repair.estimate.status}
                          </span>
                        </div>

                        <div className="space-y-1">
                          {repair.estimate.line_items?.map((item: any, i: number) => (
                            <div key={i} className="flex justify-between text-xs text-slate-300 py-0.5">
                              <span>{item.description} (x{item.quantity})</span>
                              <span className="font-mono">${item.subtotal?.toFixed(2)}</span>
                            </div>
                          ))}
                        </div>

                        <div className="flex justify-between text-sm font-bold pt-2 border-t border-slate-800 text-slate-100">
                          <span>Total Authorized Amount:</span>
                          <span className="font-mono text-emerald-400 text-base">${repair.estimate.grand_total?.toFixed(2)}</span>
                        </div>

                        {repair.estimate.status === 'draft' ? (
                          <div className="pt-2 flex items-center justify-between border-t border-slate-800">
                            <span className="text-xs text-amber-400">Your digital authorization is required to begin repair</span>
                            <button
                              onClick={() => handleCustomerApproveEstimate(repair.estimate.id)}
                              className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 text-white font-semibold text-xs flex items-center space-x-1.5 shadow-lg shadow-emerald-500/20"
                            >
                              <CheckCircle2 className="w-4 h-4" />
                              <span>Digitally Authorize & Start Work</span>
                            </button>
                          </div>
                        ) : (
                          <div className="text-xs text-emerald-400 flex items-center space-x-1 pt-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Authorized by customer. Repair work is actively proceeding.</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
                {(!customerGarage?.active_repairs || customerGarage.active_repairs.length === 0) && (
                  <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center text-xs text-slate-400">
                    No active repairs in progress for your vehicles right now.
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      ) : (
        /* ========================================================================= */
        /* WORKSHOP STAFF OPERATIONS MODE (CURRENT SYSTEM)                           */
        /* ========================================================================= */
        <>
          {/* Operational KPI Strip */}
          <section className="bg-[#0b101e] border-b border-slate-800/80 px-6 py-3">
            <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-6 gap-3">
              <div className="glass-panel p-3 rounded-xl border border-slate-800/80">
                <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Service Requests</div>
                <div className="text-xl font-bold text-slate-100 mt-0.5">{analytics?.total_service_requests ?? 0}</div>
                <div className="text-[10px] text-amber-400 mt-0.5">{analytics?.pending_review_requests ?? 0} awaiting review</div>
              </div>

              <div className="glass-panel p-3 rounded-xl border border-slate-800/80">
                <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider flex items-center justify-between">
                  <span>Safety Escalations</span>
                  <AlertTriangle className="w-3 h-3 text-red-400" />
                </div>
                <div className="text-xl font-bold text-red-400 mt-0.5">{analytics?.safety_escalations_count ?? 0}</div>
                <div className="text-[10px] text-red-300 mt-0.5">Urgent triage flagged</div>
              </div>

              <div className="glass-panel p-3 rounded-xl border border-slate-800/80">
                <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Active Work Orders</div>
                <div className="text-xl font-bold text-sky-400 mt-0.5">{analytics?.active_work_orders ?? 0}</div>
                <div className="text-[10px] text-emerald-400 mt-0.5">{analytics?.completed_work_orders ?? 0} completed</div>
              </div>

              <div className="glass-panel p-3 rounded-xl border border-slate-800/80">
                <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Bay Utilization</div>
                <div className="text-xl font-bold text-orange-400 mt-0.5">{analytics?.bay_utilization_rate ?? 0}%</div>
                <div className="text-[10px] text-slate-400 mt-0.5">{analytics?.scheduled_appointments_today ?? 0} bookings today</div>
              </div>

              <div className="glass-panel p-3 rounded-xl border border-slate-800/80">
                <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider flex items-center justify-between">
                  <span>Parts Shortages</span>
                  <AlertCircle className="w-3 h-3 text-amber-400" />
                </div>
                <div className="text-xl font-bold text-amber-400 mt-0.5">{analytics?.low_stock_parts_count ?? 0}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Below reorder line</div>
              </div>

              <div className="glass-panel p-3 rounded-xl border border-slate-800/80">
                <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider flex items-center justify-between">
                  <span>Approved Revenue</span>
                  <DollarSign className="w-3 h-3 text-emerald-400" />
                </div>
                <div className="text-xl font-bold text-emerald-400 mt-0.5">${analytics?.total_approved_revenue ?? 0}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">${analytics?.total_estimated_revenue ?? 0} estimated</div>
              </div>
            </div>
          </section>

          {/* Navigation Tabs */}
          <nav className="bg-[#090e1c] border-b border-slate-800 px-6">
            <div className="max-w-7xl mx-auto flex space-x-1 overflow-x-auto py-2">
              {[
                { id: 'intake', label: 'AI Intake & Triage', icon: Sparkles },
                { id: 'workOrders', label: 'Work Orders & Estimates', icon: Wrench },
                { id: 'scheduling', label: 'Bay Scheduling & Calendar', icon: Calendar },
                { id: 'inventory', label: 'Parts Inventory', icon: Layers },
                { id: 'weather', label: 'Weather Context', icon: CloudRain },
                { id: 'audit', label: 'Audit Trail & Automation', icon: ShieldCheck },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all whitespace-nowrap ${
                      isActive
                        ? 'bg-orange-500/15 text-orange-400 border border-orange-500/40 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-orange-400' : 'text-slate-400'}`} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </nav>

          {/* Main Content Area */}
          <main className="flex-1 max-w-7xl mx-auto w-full p-6">
            {/* ================= TAB 1: AI INTAKE & TRIAGE ================= */}
            {activeTab === 'intake' && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Column: Customer Intake Form */}
                <div className="lg:col-span-6 space-y-4">
                  <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                    <div className="flex items-center justify-between mb-3">
                      <h2 className="font-bold text-base text-slate-100 flex items-center space-x-2">
                        <Sparkles className="w-4 h-4 text-orange-400" />
                        <span>Customer Service Intake</span>
                      </h2>
                      <span className="text-xs text-slate-400 font-mono">Unstructured Message Ingestion</span>
                    </div>

                    {/* Preset Scenario Quick-Pick Buttons */}
                    <div className="mb-4">
                      <span className="text-xs font-semibold text-slate-400 block mb-2">SRS Demo Scenarios:</span>
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => applyPreset('brake_emergency')}
                          className="text-left px-3 py-2 rounded-lg bg-red-950/30 hover:bg-red-950/50 border border-red-500/30 text-red-200 text-xs font-medium transition-colors"
                        >
                          <div className="font-bold flex items-center space-x-1.5 text-red-400">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            <span>Brake Failure / Spongy</span>
                          </div>
                          <div className="text-[10px] text-slate-400 truncate">2021 Toyota Camry (SRS Section 18)</div>
                        </button>

                        <button
                          onClick={() => applyPreset('oil_maintenance')}
                          className="text-left px-3 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-medium transition-colors"
                        >
                          <div className="font-bold text-sky-400">Routine Maintenance</div>
                          <div className="text-[10px] text-slate-400 truncate">2022 Subaru Outback 30k Oil</div>
                        </button>

                        <button
                          onClick={() => applyPreset('check_engine')}
                          className="text-left px-3 py-2 rounded-lg bg-amber-950/30 hover:bg-amber-950/50 border border-amber-500/30 text-amber-200 text-xs font-medium transition-colors"
                        >
                          <div className="font-bold text-amber-400">Check Engine Warning</div>
                          <div className="text-[10px] text-slate-400 truncate">2019 BMW 330i Rough Idle</div>
                        </button>

                        <button
                          onClick={() => applyPreset('ceramic_coating')}
                          className="text-left px-3 py-2 rounded-lg bg-emerald-950/30 hover:bg-emerald-950/50 border border-emerald-500/30 text-emerald-200 text-xs font-medium transition-colors"
                        >
                          <div className="font-bold text-emerald-400">Detailing & Wash</div>
                          <div className="text-[10px] text-slate-400 truncate">2023 Tesla Model 3 Ceramic Shield</div>
                        </button>
                      </div>
                    </div>

                    {/* Customer Contact & Vehicle Quick Fields */}
                    <div className="grid grid-cols-3 gap-3 mb-3">
                      <div>
                        <label className="text-xs text-slate-400 block mb-1">Customer Name</label>
                        <input
                          type="text"
                          placeholder="e.g. Alex Mercer"
                          value={customerName}
                          onChange={(e) => setCustomerName(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-orange-500"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-slate-400 block mb-1">Email Address</label>
                        <input
                          type="email"
                          placeholder="alex.mercer@example.com"
                          value={customerEmail}
                          onChange={(e) => setCustomerEmail(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-orange-500"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-slate-400 block mb-1">Phone / Mobile</label>
                        <input
                          type="text"
                          placeholder="415-555-0199"
                          value={customerPhone}
                          onChange={(e) => setCustomerPhone(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-orange-500"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-3">
                      <div>
                        <label className="text-xs text-slate-400 block mb-1">Vehicle Make</label>
                        <input
                          type="text"
                          placeholder="Toyota"
                          value={vehicleMake}
                          onChange={(e) => setVehicleMake(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-orange-500"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-slate-400 block mb-1">Model</label>
                        <input
                          type="text"
                          placeholder="Camry"
                          value={vehicleModel}
                          onChange={(e) => setVehicleModel(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-orange-500"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-slate-400 block mb-1">Year</label>
                        <input
                          type="number"
                          placeholder="2021"
                          value={vehicleYear}
                          onChange={(e) => setVehicleYear(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-orange-500"
                        />
                      </div>
                    </div>

                    {/* Customer Message Area */}
                    <div className="mb-4">
                      <label className="text-xs text-slate-400 block mb-1">Customer Description / Complaint</label>
                      <textarea
                        rows={4}
                        placeholder="Describe vehicle symptoms, sounds, warning lights, or maintenance requests..."
                        value={intakeMessage}
                        onChange={(e) => setIntakeMessage(e.target.value)}
                        className="w-full px-3 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-sm focus:outline-none focus:border-orange-500"
                      />
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={handleAnalyzeIntake}
                        disabled={loading}
                        className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-semibold text-sm shadow-lg shadow-orange-500/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
                      >
                        <Sparkles className="w-4 h-4" />
                        <span>Run AI Agent Extraction</span>
                      </button>
                      <button
                        onClick={handleSaveRequest}
                        disabled={loading || !intakeMessage}
                        className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm border border-slate-700 flex items-center space-x-1.5 transition-colors disabled:opacity-50"
                      >
                        <FileText className="w-4 h-4 text-slate-400" />
                        <span>Persist & Email Customer</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Right Column: AI Extraction, Safety Guardrails & Clarification */}
                <div className="lg:col-span-6 space-y-4">
                  {aiExtraction ? (
                    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="font-bold text-base text-slate-100 flex items-center space-x-2">
                          <ShieldCheck className="w-4 h-4 text-sky-400" />
                          <span>Structured AI Service Extraction</span>
                        </h3>
                        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                          Confidence: {(aiExtraction.ai_confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>

                      {/* Safety Escalation Alert Banner */}
                      {aiExtraction.safety_escalation && (
                        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/50 text-red-200">
                          <div className="flex items-center space-x-2 text-red-400 font-bold text-sm mb-1">
                            <AlertTriangle className="w-4 h-4 text-red-400 animate-bounce" />
                            <span>SAFETY-CRITICAL ESCALATION TRIGGERED</span>
                          </div>
                          <p className="text-xs text-red-300 leading-relaxed font-sans">
                            {aiExtraction.safety_advisory}
                          </p>
                        </div>
                      )}

                      {/* Extraction Metrics Grid */}
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                          <span className="text-slate-400 block mb-0.5">Proposed Service Category</span>
                          <span className="font-bold text-slate-200 uppercase tracking-wide">
                            {aiExtraction.proposed_service_type?.replace(/_/g, ' ')}
                          </span>
                        </div>

                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                          <span className="text-slate-400 block mb-0.5">Estimated Duration</span>
                          <span className="font-bold text-orange-400">
                            {aiExtraction.estimated_duration_minutes} minutes
                          </span>
                        </div>

                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                          <span className="text-slate-400 block mb-0.5">Identified Vehicle</span>
                          <span className="font-bold text-slate-200">
                            {aiExtraction.vehicle_year || 'Year'} {aiExtraction.vehicle_make || 'Make'} {aiExtraction.vehicle_model || 'Model'}
                          </span>
                        </div>

                        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                          <span className="text-slate-400 block mb-0.5">Triage Urgency</span>
                          <span className={`font-bold uppercase ${aiExtraction.urgency === 'safety_critical' ? 'text-red-400' : 'text-emerald-400'}`}>
                            {aiExtraction.urgency}
                          </span>
                        </div>
                      </div>

                      {/* Identified Symptoms List */}
                      <div>
                        <span className="text-xs font-semibold text-slate-400 block mb-1.5">Parsed Symptoms & Indicators:</span>
                        <div className="space-y-1">
                          {aiExtraction.symptoms?.map((sym: string, i: number) => (
                            <div key={i} className="flex items-center space-x-2 text-xs text-slate-300 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800/80">
                              <CheckCircle2 className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                              <span>{sym}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Recommended Parts List */}
                      <div>
                        <span className="text-xs font-semibold text-slate-400 block mb-1.5">Recommended Parts / Materials:</span>
                        <div className="flex flex-wrap gap-1.5">
                          {aiExtraction.recommended_parts?.map((part: string, i: number) => (
                            <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-orange-500/10 text-orange-300 border border-orange-500/20">
                              {part}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Clarification Questions Dialog */}
                      {aiExtraction.clarification_questions?.length > 0 && (
                        <div className="p-3.5 rounded-xl bg-sky-950/30 border border-sky-500/30">
                          <div className="text-xs font-bold text-sky-400 flex items-center space-x-1.5 mb-1.5">
                            <AlertCircle className="w-3.5 h-3.5" />
                            <span>AI Intake Clarification Question:</span>
                          </div>
                          <p className="text-xs text-sky-200 mb-2">
                            {aiExtraction.clarification_questions[0]}
                          </p>
                          {activeRequestId && (
                            <div className="flex items-center space-x-2">
                              <input
                                type="text"
                                placeholder="Type customer reply..."
                                value={clarificationInput}
                                onChange={(e) => setClarificationInput(e.target.value)}
                                className="flex-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
                              />
                              <button
                                onClick={handleClarificationAnswer}
                                className="px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold"
                              >
                                Send
                              </button>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Work Order Conversion Trigger */}
                      <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                        <span className="text-xs text-slate-400">
                          {activeRequestId ? `Draft Request #${activeRequestId} persisted` : 'Save request to convert'}
                        </span>
                        <button
                          onClick={handleConvertToWorkOrder}
                          disabled={!activeRequestId}
                          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center space-x-1.5 transition-colors disabled:opacity-40"
                        >
                          <UserCheck className="w-4 h-4" />
                          <span>Approve & Convert to Work Order</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center flex flex-col items-center justify-center space-y-3 min-h-[380px]">
                      <div className="w-12 h-12 rounded-2xl bg-slate-800/80 flex items-center justify-center text-slate-500 border border-slate-700">
                        <Sparkles className="w-6 h-6 text-slate-400" />
                      </div>
                      <h3 className="font-bold text-slate-200">AI Extraction Pending</h3>
                      <p className="text-xs text-slate-400 max-w-sm">
                        Enter customer message or select one of the SRS demo presets on the left, then click <b>Run AI Agent Extraction</b> to preview triage, duration, and safety guardrails.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ================= TAB 2: WORK ORDERS & ESTIMATES ================= */}
            {activeTab === 'workOrders' && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Work Orders List */}
                <div className="lg:col-span-5 space-y-3">
                  <div className="glass-panel p-4 rounded-2xl border border-slate-800">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-sm text-slate-100 flex items-center space-x-2">
                        <Wrench className="w-4 h-4 text-orange-400" />
                        <span>Workshop Operational Work Orders</span>
                      </h3>
                      <span className="text-xs text-slate-400">{workOrders.length} records</span>
                    </div>

                    <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
                      {workOrders.map((wo) => {
                        const isSelected = selectedWorkOrder?.id === wo.id;
                        return (
                          <div
                            key={wo.id}
                            onClick={() => handleSelectWorkOrder(wo.id)}
                            className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                              isSelected
                                ? 'bg-orange-500/10 border-orange-500/50 shadow-md'
                                : 'bg-slate-900/60 hover:bg-slate-900 border-slate-800/80'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="font-bold text-xs text-slate-200">Work Order #{wo.id}</span>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                                wo.status === 'completed'
                                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                  : wo.status === 'scheduled'
                                  ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                                  : wo.status === 'in_progress'
                                  ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                              }`}>
                                {wo.status.replace(/_/g, ' ')}
                              </span>
                            </div>
                            <div className="text-xs text-slate-300 font-medium mb-1">
                              {wo.service_type?.replace(/_/g, ' ').toUpperCase()}
                            </div>
                            <div className="text-[11px] text-slate-400 truncate">
                              {wo.customer_complaint || 'No complaint notes'}
                            </div>
                          </div>
                        );
                      })}
                      {workOrders.length === 0 && (
                        <div className="text-center py-8 text-xs text-slate-500">No work orders recorded yet.</div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Work Order Detail & Human-in-the-Loop Estimate Approval */}
                <div className="lg:col-span-7 space-y-4">
                  {selectedWorkOrder ? (
                    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                        <div>
                          <h3 className="font-bold text-base text-slate-100">
                            Work Order #{selectedWorkOrder.id}: {selectedWorkOrder.service_type?.replace(/_/g, ' ').toUpperCase()}
                          </h3>
                          <p className="text-xs text-slate-400 mt-0.5">
                            Customer: {selectedWorkOrder.customer?.name || 'Walk-in'} | Vehicle: {selectedWorkOrder.vehicle ? `${selectedWorkOrder.vehicle.year} ${selectedWorkOrder.vehicle.make} ${selectedWorkOrder.vehicle.model}` : 'Not specified'}
                          </p>
                        </div>
                        <span className="text-xs font-mono px-3 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
                          Est. {selectedWorkOrder.estimated_duration_minutes} min
                        </span>
                      </div>

                      {/* Complaint & Mechanic Notes */}
                      <div className="space-y-3">
                        <div>
                          <span className="text-xs font-semibold text-slate-400 block mb-1">Customer Reported Concern:</span>
                          <p className="text-xs text-slate-300 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                            {selectedWorkOrder.customer_complaint || 'None'}
                          </p>
                        </div>

                        <div>
                          <span className="text-xs font-semibold text-slate-400 block mb-1">Technician Inspection & Service Notes:</span>
                          <textarea
                            rows={3}
                            value={mechanicNotes}
                            onChange={(e) => setMechanicNotes(e.target.value)}
                            placeholder="Add mechanic diagnosis, pad thickness measurements, fluid condition, torque values..."
                            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-orange-500"
                          />
                        </div>
                      </div>

                      {/* Estimate Section (Human-in-the-Loop Approval FR-10) */}
                      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <DollarSign className="w-4 h-4 text-emerald-400" />
                            <span className="font-bold text-sm text-slate-200">Formal Workshop Estimate</span>
                          </div>
                          {selectedWorkOrder.estimate ? (
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                              selectedWorkOrder.estimate.status === 'approved'
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            }`}>
                              {selectedWorkOrder.estimate.status}
                            </span>
                          ) : (
                            <button
                              onClick={() => handleGenerateEstimate(selectedWorkOrder.id)}
                              className="px-3 py-1 rounded-lg bg-orange-600 hover:bg-orange-500 text-white text-xs font-semibold"
                            >
                              Calculate Draft Estimate
                            </button>
                          )}
                        </div>

                        {selectedWorkOrder.estimate && (
                          <div className="space-y-2">
                            <div className="space-y-1">
                              {selectedWorkOrder.estimate.line_items?.map((item: any, i: number) => (
                                <div key={i} className="flex justify-between text-xs text-slate-300 py-1 border-b border-slate-800/50">
                                  <span>{item.description} (x{item.quantity})</span>
                                  <span className="font-mono text-slate-200">${item.subtotal?.toFixed(2)}</span>
                                </div>
                              ))}
                            </div>

                            <div className="flex justify-between text-sm font-bold pt-2 text-slate-100">
                              <span>Grand Total (Labor + Parts):</span>
                              <span className="font-mono text-emerald-400">${selectedWorkOrder.estimate.grand_total?.toFixed(2)}</span>
                            </div>

                            {selectedWorkOrder.estimate.status === 'draft' ? (
                              <div className="pt-2 flex items-center justify-between border-t border-slate-800">
                                <span className="text-xs text-amber-400 flex items-center space-x-1">
                                  <AlertCircle className="w-3.5 h-3.5" />
                                  <span>Requires human advisor approval before service start</span>
                                </span>
                                <button
                                  onClick={() => handleApproveEstimate(selectedWorkOrder.estimate.id, selectedWorkOrder.id)}
                                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center space-x-1"
                                >
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  <span>Authorize Estimate (Human-in-the-Loop)</span>
                                </button>
                              </div>
                            ) : (
                              <div className="text-xs text-slate-400">
                                Authorized by <b className="text-slate-200">{selectedWorkOrder.estimate.approver_name}</b> under policy.
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Lifecycle Status Transitions */}
                      <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                        <span className="text-xs text-slate-400">Update State:</span>
                        <div className="flex space-x-2">
                          {['scheduled', 'in_progress', 'completed'].map((st) => (
                            <button
                              key={st}
                              onClick={() => handleUpdateWorkOrderStatus(selectedWorkOrder.id, st)}
                              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors ${
                                selectedWorkOrder.status === st
                                  ? 'bg-orange-500 text-white'
                                  : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                              }`}
                            >
                              {st.replace(/_/g, ' ')}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center flex flex-col items-center justify-center space-y-3 min-h-[350px]">
                      <Wrench className="w-8 h-8 text-slate-600" />
                      <p className="text-xs text-slate-400">Select a work order from the list on the left to inspect details and authorize estimates.</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ================= TAB 3: SCHEDULING & BAY AVAILABILITY ================= */}
            {activeTab === 'scheduling' && (
              <div className="space-y-6">
                {/* Filter Bar */}
                <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center space-x-3">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Service Type</label>
                      <select
                        value={selectedServiceType}
                        onChange={(e) => setSelectedServiceType(e.target.value)}
                        className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-orange-500"
                      >
                        <option value="brake_service">Brake Service (Heavy Lift)</option>
                        <option value="oil_change">Oil Change & Lube (Express Bay)</option>
                        <option value="engine_diagnostics">Engine Diagnostics (OBD Bay)</option>
                        <option value="detailing_and_wash">Detailing & Ceramic (Wash Studio)</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Target Date</label>
                      <input
                        type="date"
                        value={selectedDate}
                        onChange={(e) => setSelectedDate(e.target.value)}
                        className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-orange-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Target Work Order</label>
                      <select
                        value={bookingWoId || ''}
                        onChange={(e) => setBookingWoId(e.target.value ? parseInt(e.target.value) : null)}
                        className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-orange-500"
                      >
                        <option value="">Select Work Order...</option>
                        {workOrders.map((wo) => (
                          <option key={wo.id} value={wo.id}>
                            WO #{wo.id} - {wo.service_type}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <button
                    onClick={handleSearchSlots}
                    disabled={loading}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 text-white font-semibold text-xs flex items-center space-x-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Re-query Deterministic Slots</span>
                  </button>
                </div>

                {/* Feasible Capacity Slots Matrix */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-bold text-sm text-slate-200 flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-orange-400" />
                      <span>Feasible Certified Slots for {selectedDate}</span>
                    </h3>
                    <span className="text-xs text-slate-400">Deterministic Skill & Bay Verification Active</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    {availableSlots.map((slot, i) => (
                      <div
                        key={i}
                        className={`p-4 rounded-xl border transition-all ${
                          slot.available
                            ? 'bg-slate-900/80 border-slate-700/80 hover:border-orange-500/60'
                            : 'bg-slate-950/40 border-slate-800 opacity-50'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-mono text-sm font-bold text-slate-100">
                            {new Date(slot.start_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            slot.available
                              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                              : 'bg-red-500/20 text-red-400 border border-red-500/30'
                          }`}>
                            {slot.available ? 'Available' : 'Booked'}
                          </span>
                        </div>

                        <div className="text-xs text-slate-300 font-medium mb-1">{slot.bay_name}</div>
                        <div className="text-xs text-slate-400 mb-2">Tech: {slot.mechanic_name}</div>
                        <div className="text-[10px] text-slate-500 italic mb-3">{slot.reason}</div>

                        {slot.available && (
                          <button
                            onClick={() => handleConfirmAppointment(slot)}
                            className="w-full py-1.5 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-semibold text-xs transition-colors"
                          >
                            Confirm Slot (Idempotent)
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Active Bookings & Calendar Sync Recovery Section */}
                <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-sm text-slate-200">Active Scheduled Appointments & Calendar Events</h3>
                      <p className="text-xs text-slate-400">Includes Google Calendar sync status and intentional resilience recovery simulation (SRS FR-08 / FR-15).</p>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-2.5 px-3">Appointment ID</th>
                          <th className="py-2.5 px-3">Time Window</th>
                          <th className="py-2.5 px-3">Service Bay</th>
                          <th className="py-2.5 px-3">Technician</th>
                          <th className="py-2.5 px-3">Sync Status</th>
                          <th className="py-2.5 px-3 text-right">Resilience Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {scheduledAppointments.map((app) => (
                          <tr key={app.id} className="hover:bg-slate-900/50">
                            <td className="py-2.5 px-3 font-mono font-bold text-slate-300">#{app.id} (WO #{app.work_order_id})</td>
                            <td className="py-2.5 px-3 font-mono text-slate-300">
                              {new Date(app.start_at).toLocaleDateString()} {new Date(app.start_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </td>
                            <td className="py-2.5 px-3 text-slate-300">{app.bay_name}</td>
                            <td className="py-2.5 px-3 text-slate-300">{app.mechanic_name}</td>
                            <td className="py-2.5 px-3">
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                                app.calendar_sync_status === 'synced'
                                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                  : 'bg-red-500/20 text-red-400 border border-red-500/30'
                              }`}>
                                {app.calendar_sync_status}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-right space-x-2">
                              <button
                                onClick={() => handleCalendarSyncTest(app.id, false)}
                                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium border border-slate-700"
                              >
                                Sync OK
                              </button>
                              <button
                                onClick={() => handleCalendarSyncTest(app.id, true)}
                                className="px-2.5 py-1 rounded bg-red-950/40 hover:bg-red-950/60 text-red-400 text-[11px] font-medium border border-red-500/30"
                              >
                                Trigger 503 Failure
                              </button>
                            </td>
                          </tr>
                        ))}
                        {scheduledAppointments.length === 0 && (
                          <tr>
                            <td colSpan={6} className="py-6 text-center text-slate-500">No appointments confirmed yet.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ================= TAB 4: PARTS INVENTORY ================= */}
            {activeTab === 'inventory' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-base text-slate-100 flex items-center space-x-2">
                      <Layers className="w-5 h-5 text-orange-400" />
                      <span>Workshop Parts & Inventory Management</span>
                    </h3>
                    <p className="text-xs text-slate-400">Live stock tracking, reorder thresholds, and material cost controls.</p>
                  </div>

                  {/* Quick Restock Dialog */}
                  <div className="flex items-center space-x-2">
                    <select
                      value={restockPartId || ''}
                      onChange={(e) => setRestockPartId(e.target.value ? parseInt(e.target.value) : null)}
                      className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-orange-500"
                    >
                      <option value="">Select Part to Restock...</option>
                      {parts.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name} ({p.sku})
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min="1"
                      value={restockQty}
                      onChange={(e) => setRestockQty(parseInt(e.target.value) || 1)}
                      className="w-16 px-2 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200"
                    />
                    <button
                      onClick={handleRestockPart}
                      disabled={!restockPartId}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold disabled:opacity-50"
                    >
                      Restock
                    </button>
                  </div>
                </div>

                {/* Parts Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {parts.map((part) => (
                    <div
                      key={part.id}
                      className={`glass-panel p-4 rounded-xl border transition-all ${
                        part.is_low_stock ? 'border-amber-500/50 bg-amber-950/10' : 'border-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-mono text-xs text-slate-400">{part.sku}</span>
                        {part.is_low_stock && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center space-x-1">
                            <AlertCircle className="w-3 h-3" />
                            <span>Low Stock</span>
                          </span>
                        )}
                      </div>

                      <h4 className="font-bold text-sm text-slate-200 mb-1">{part.name}</h4>
                      <div className="text-xs text-slate-400 capitalize mb-3">Category: {part.category}</div>

                      <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
                        <div>
                          <span className="text-slate-400 block text-[10px]">On Hand / Min</span>
                          <span className="font-bold text-slate-200 font-mono">
                            {part.quantity_on_hand} <span className="text-slate-500 font-normal">/ {part.reorder_threshold}</span>
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-slate-400 block text-[10px]">Retail Price</span>
                          <span className="font-bold text-emerald-400 font-mono">${part.unit_price?.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ================= TAB 5: WEATHER CONTEXT ================= */}
            {activeTab === 'weather' && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-6 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
                        <CloudRain className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-base text-slate-100">Live Weather Context</h3>
                        <p className="text-xs text-slate-400">{weatherData?.location || 'San Francisco, CA'}</p>
                      </div>
                    </div>
                    <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 text-slate-400">
                      Open-Meteo API
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-3 pt-2">
                    <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                      <span className="text-xs text-slate-400 block mb-1">Temperature</span>
                      <span className="text-xl font-bold text-slate-100 font-mono">{weatherData?.temperature_c ?? 18.5}°C</span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                      <span className="text-xs text-slate-400 block mb-1">Condition</span>
                      <span className="text-sm font-bold text-sky-400">{weatherData?.weather_condition ?? 'Clear'}</span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
                      <span className="text-xs text-slate-400 block mb-1">Rain Risk</span>
                      <span className="text-xl font-bold text-amber-400 font-mono">{weatherData?.precipitation_probability ?? 10}%</span>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-sky-950/30 border border-sky-500/30 text-xs text-sky-200 leading-relaxed">
                    <span className="font-bold block text-sky-400 mb-1">Automated Workshop Scheduling Advisory:</span>
                    {weatherData?.advisory_for_service || 'Favorable weather conditions. Exterior detailing, paint curing, and post-repair brake road tests can proceed safely without rain degradation.'}
                  </div>
                </div>

                <div className="lg:col-span-6 glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
                  <h3 className="font-bold text-base text-slate-100">Weather-Sensitive Workflow Policies (SRS FR-11)</h3>
                  <ul className="space-y-2 text-xs text-slate-300">
                    <li className="flex items-start space-x-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Exterior ceramic coating & detailing requires &lt;35% precipitation probability for optimal curing.</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>High-speed brake post-service road testing requires wet-road alerts when precipitation exceeds 50%.</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Weather context grounds AI recommendations without independently making financial or safety decisions.</span>
                    </li>
                  </ul>
                </div>
              </div>
            )}

            {/* ================= TAB 6: AUDIT TRAIL & AUTOMATION ================= */}
            {activeTab === 'audit' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-base text-slate-100 flex items-center space-x-2">
                      <ShieldCheck className="w-5 h-5 text-orange-400" />
                      <span>Immutable Operational Audit Trail & Proactive Jobs</span>
                    </h3>
                    <p className="text-xs text-slate-400">Traceability for every AI tool call, estimate authorization, and status mutation.</p>
                  </div>

                  <button
                    onClick={handleRunAutomation}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 text-white font-semibold text-xs flex items-center space-x-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Run Proactive Automation Cycle</span>
                  </button>
                </div>

                {/* Audit Events Table */}
                <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-2 px-3">Timestamp</th>
                          <th className="py-2 px-3">Actor / Role</th>
                          <th className="py-2 px-3">Action</th>
                          <th className="py-2 px-3">Entity</th>
                          <th className="py-2 px-3">Correlation / Details</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 font-mono">
                        {auditEvents.map((ev) => (
                          <tr key={ev.id} className="hover:bg-slate-900/50">
                            <td className="py-2.5 px-3 text-slate-400">{new Date(ev.timestamp).toLocaleTimeString()}</td>
                            <td className="py-2.5 px-3 text-slate-200">
                              {ev.actor_id} <span className="text-slate-500 text-[10px]">({ev.actor_role})</span>
                            </td>
                            <td className="py-2.5 px-3 font-semibold text-orange-400">{ev.action}</td>
                            <td className="py-2.5 px-3 text-slate-300">{ev.entity_type} #{ev.entity_id}</td>
                            <td className="py-2.5 px-3 text-slate-400 text-[11px] truncate max-w-xs">
                              {JSON.stringify(ev.metadata_json)}
                            </td>
                          </tr>
                        ))}
                        {auditEvents.length === 0 && (
                          <tr>
                            <td colSpan={5} className="py-6 text-center text-slate-500 font-sans">No audit events recorded.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </main>
        </>
      )}

      {/* ========================================================================= */}
      {/* REAL-TIME EMAIL NOTIFICATIONS OUTBOX MODAL                                */}
      {/* ========================================================================= */}
      {showEmailModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-[#0b1222] border border-sky-500/40 rounded-3xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
                  <Mail className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-100">Live Dispatched Email Outbox</h3>
                  <p className="text-[11px] text-slate-400">Review all transactional HTML emails sent to vehicle owners</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowEmailModal(false);
                  setSelectedEmail(null);
                }}
                className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 grid grid-cols-1 md:grid-cols-12 overflow-hidden">
              {/* Emails List */}
              <div className="md:col-span-5 border-r border-slate-800 overflow-y-auto p-3 space-y-2 bg-[#090e1c]">
                {emailNotifications.map((em) => {
                  const isSel = selectedEmail?.id === em.id;
                  return (
                    <div
                      key={em.id}
                      onClick={() => setSelectedEmail(em)}
                      className={`p-3 rounded-xl border transition-all cursor-pointer ${
                        isSel
                          ? 'bg-sky-500/15 border-sky-500/60 shadow-md'
                          : 'bg-slate-900/60 hover:bg-slate-900 border-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] uppercase font-bold text-sky-400 px-2 py-0.5 rounded-full bg-sky-500/10 border border-sky-500/20">
                          {em.notification_type?.replace(/_/g, ' ')}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {new Date(em.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <h4 className="text-xs font-bold text-slate-200 truncate">{em.subject}</h4>
                      <p className="text-[11px] text-slate-400 truncate mt-0.5">To: {em.recipient_email}</p>
                    </div>
                  );
                })}
                {emailNotifications.length === 0 && (
                  <div className="text-center py-12 text-xs text-slate-500">No emails dispatched yet.</div>
                )}
              </div>

              {/* Email HTML Preview */}
              <div className="md:col-span-7 p-5 overflow-y-auto bg-[#070b14] space-y-3">
                {selectedEmail ? (
                  <div className="space-y-3">
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1">
                      <div><b className="text-slate-400">Subject:</b> <span className="text-slate-200 font-bold">{selectedEmail.subject}</span></div>
                      <div><b className="text-slate-400">Recipient:</b> <span className="text-sky-400 font-mono">{selectedEmail.recipient_email}</span></div>
                      <div><b className="text-slate-400">Sent At:</b> <span className="text-slate-300 font-mono">{new Date(selectedEmail.created_at).toLocaleString()}</span></div>
                    </div>
                    <div
                      className="rounded-2xl overflow-hidden border border-slate-800 p-2 bg-[#0c1222]"
                      dangerouslySetInnerHTML={{ __html: selectedEmail.content_html }}
                    />
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500 text-xs">
                    <Inbox className="w-8 h-8 text-slate-600 mb-2" />
                    <p>Select any email message on the left to preview the formatted HTML template.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
