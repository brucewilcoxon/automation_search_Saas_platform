import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import Index from "./pages/Index";
import SearchPage from "./pages/SearchPage";
import AuctionDetailPage from "./pages/AuctionDetailPage";
import ParcelDetailPage from "./pages/ParcelDetailPage";
import CashBuyersPage from "./pages/CashBuyersPage";
import LettersPage from "./pages/LettersPage";
import RunsPage from "./pages/RunsPage";
import SettingsPage from "./pages/SettingsPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Index />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/auction/:id" element={<AuctionDetailPage />} />
            <Route path="/parcel/:parcelId" element={<ParcelDetailPage />} />
            <Route path="/tools/cash-buyers" element={<CashBuyersPage />} />
            <Route path="/tools/letters" element={<LettersPage />} />
            <Route path="/runs" element={<RunsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
