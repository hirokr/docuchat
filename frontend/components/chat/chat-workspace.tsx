"use client";

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";
import { usePanelRef } from "react-resizable-panels";
import {
  Brain,
  ChevronLeft,
  ChevronRight,
  Copy,
  FileStack,
  FileText,
  FileType,
  Highlighter,
  Languages,
  LayoutTemplate,
  Link2,
  Loader2,
  Maximize,
  MessageCircle,
  X,
  MessageSquare,
  MoreVertical,
  PanelLeft,
  PanelRight,
  Paperclip,
  Pencil,
  Plus,
  ScanSearch,
  Search,
  Send,
  Settings,
  Share2,
  Sparkles,
  StickyNote,
  ThumbsUp,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const USER_AVATAR =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAMLUdYKF_eeUZueFP_jacoTYM-i2UXcbEF5hNiIBC9HlKGUCCbkL2XAh8u0IwtRpcOeBNWnbrA2jZ-VRYHT7QJw15F9KnJ-pPX59k8mtxKFHVYs0m5yYuCKW71re1MmR6Etf-IpZvqvMyXuv5fgIEfTIoauxDXrKEY76gkyviYlJiGqCphJP0pKLhwhF53Pf_l7y8hZSJM40YghLwFOBhDBOwpPfjcliL4JRZnCRC6HRA6zHyVZzmMfiOrL4Pew4C19QRub6RqBYQ";

const DOCUMENTS = [
  { id: "research", name: "Research_Paper_v1.pdf", active: true },
  { id: "annual", name: "Annual_Report.pdf", active: false },
] as const;

const WORKSPACE_LINKS = [
  { icon: MessageSquare, label: "Chat History" },
  { icon: LayoutTemplate, label: "Templates" },
] as const;

const QUICK_ACTIONS = [
  { icon: FileStack, label: "Summarize" },
  { icon: ScanSearch, label: "Extract Data" },
  { icon: Languages, label: "Translate" },
] as const;

function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    const onChange = () => setMatches(media.matches);
    onChange();
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, [query]);

  return matches;
}

function SidebarToggle({
  side,
  collapsed,
  onToggle,
  className,
}: {
  side: "left" | "right";
  collapsed: boolean;
  onToggle: () => void;
  className?: string;
}) {
  const Icon = side === "left" ? PanelLeft : PanelRight;
  const label =
    side === "left"
      ? collapsed
        ? "Expand documents sidebar"
        : "Collapse documents sidebar"
      : collapsed
        ? "Expand PDF viewer"
        : "Collapse PDF viewer";

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          onClick={onToggle}
          aria-label={label}
          className={cn(
            "absolute top-4 z-20 text-on-surface-variant hover:text-primary",
            side === "left" ? "right-1" : "left-1",
            className
          )}
        >
          <Icon className="size-4" />
        </Button>
      </TooltipTrigger>
      <TooltipContent side={side === "left" ? "right" : "left"}>
        {label}
      </TooltipContent>
    </Tooltip>
  );
}

function CitationChip({ page }: { page: number }) {
  return (
    <button
      type="button"
      className="inline-flex items-center gap-1 rounded-full border border-outline-variant/30 bg-surface-container-high px-2 py-0.5 text-[10px] text-primary transition-all hover:bg-primary/10"
    >
      <Link2 className="size-3" aria-hidden />
      Page {page}
    </button>
  );
}

function NavSidebar({
  collapsed,
  selectedDocId,
  onSelectDoc,
}: {
  collapsed: boolean;
  selectedDocId: string;
  onSelectDoc: (id: string) => void;
}) {
  return (
    <div className="relative flex h-full flex-col border-r border-outline-variant/20 bg-surface-container">
      {!collapsed && (
        <div className="flex items-center gap-3 px-6 py-8">
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary">
            <Brain className="size-5 text-on-primary" aria-hidden />
          </div>
          <h1 className="text-headline-sm font-semibold text-on-surface">
            DocuChat
          </h1>
        </div>
      )}

      {collapsed && (
        <div className="flex justify-center py-6">
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary">
            <Brain className="size-5 text-on-primary" aria-hidden />
          </div>
        </div>
      )}

      <div className={cn("mb-6 px-4", collapsed && "px-2")}>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              className={cn(
                "w-full gap-2 rounded-xl bg-primary-container py-3 text-label-md font-semibold text-on-primary-container hover:opacity-90",
                collapsed && "size-10 px-0"
              )}
              size={collapsed ? "icon" : "default"}
            >
              <Plus className="size-5 shrink-0" aria-hidden />
              {!collapsed && "Upload PDF"}
            </Button>
          </TooltipTrigger>
          {collapsed && <TooltipContent side="right">Upload PDF</TooltipContent>}
        </Tooltip>
      </div>

      <ScrollArea className="flex-1 chat-scrollbar">
        <nav className="space-y-1 px-2 pb-4">
          {!collapsed && (
            <div className="px-4 py-2">
              <span className="text-label-md font-semibold tracking-wide text-on-surface-variant uppercase">
                Documents
              </span>
            </div>
          )}

          {DOCUMENTS.map((doc) => {
            const isActive = doc.id === selectedDocId;
            return (
              <Tooltip key={doc.id}>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    onClick={() => onSelectDoc(doc.id)}
                    className={cn(
                      "group mx-2 my-1 flex w-[calc(100%-16px)] cursor-pointer items-center gap-3 rounded-lg px-4 py-3 transition-all",
                      collapsed && "justify-center px-2",
                      isActive
                        ? "bg-secondary-container text-on-secondary-container"
                        : "text-on-surface-variant hover:bg-surface-container-high"
                    )}
                  >
                    <FileText className="size-5 shrink-0" aria-hidden />
                    {!collapsed && (
                      <>
                        <span
                          className={cn(
                            "truncate",
                            !isActive && "text-body-sm"
                          )}
                        >
                          {doc.name}
                        </span>
                        <MoreVertical
                          className="ml-auto size-[18px] opacity-0 transition-opacity group-hover:opacity-100"
                          aria-hidden
                        />
                      </>
                    )}
                  </button>
                </TooltipTrigger>
                {collapsed && (
                  <TooltipContent side="right">{doc.name}</TooltipContent>
                )}
              </Tooltip>
            );
          })}

          {!collapsed && (
            <div className="px-4 pt-6 pb-2">
              <span className="text-label-md font-semibold tracking-wide text-on-surface-variant uppercase">
                Workspace
              </span>
            </div>
          )}

          {WORKSPACE_LINKS.map(({ icon: Icon, label }) => (
            <Tooltip key={label}>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className={cn(
                    "mx-2 my-1 flex cursor-pointer items-center gap-3 rounded-lg px-4 py-3 text-on-surface-variant transition-all hover:bg-surface-container-high",
                    collapsed && "justify-center px-2"
                  )}
                >
                  <Icon className="size-5 shrink-0" aria-hidden />
                  {!collapsed && (
                    <span className="text-body-sm">{label}</span>
                  )}
                </button>
              </TooltipTrigger>
              {collapsed && (
                <TooltipContent side="right">{label}</TooltipContent>
              )}
            </Tooltip>
          ))}
        </nav>
      </ScrollArea>

      <div className="border-t border-outline-variant/10 p-4">
        <button
          type="button"
          className={cn(
            "flex w-full cursor-pointer items-center gap-3 rounded-lg p-2 transition-all hover:bg-surface-container-high",
            collapsed && "justify-center"
          )}
        >
          <div className="relative size-10 shrink-0 overflow-hidden rounded-full border border-outline-variant/30 bg-surface-variant">
            <Image
              src={USER_AVATAR}
              alt="Alex Chen"
              fill
              className="object-cover"
              sizes="40px"
            />
          </div>
          {!collapsed && (
            <>
              <div className="flex min-w-0 flex-col text-left">
                <span className="text-body-sm font-semibold text-on-surface">
                  Alex Chen
                </span>
                <span className="text-label-md text-on-surface-variant">
                  Pro Plan
                </span>
              </div>
              <Settings
                className="ml-auto size-5 text-on-surface-variant"
                aria-hidden
              />
            </>
          )}
        </button>
      </div>
    </div>
  );
}

function ChatPanel({ onOpenPdf }: { onOpenPdf?: () => void }) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const resizeTextarea = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 192)}px`;
  }, []);

  return (
    <div className="flex h-full min-w-0 flex-1 flex-col border-r border-outline-variant/20 bg-background">
      <header className="flex items-center justify-between border-b border-outline-variant/10 px-6 py-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="size-5 text-primary" aria-hidden />
          <h2 className="text-headline-sm font-semibold">Research Assistant</h2>
        </div>
        <div className="flex items-center gap-1">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="text-on-surface-variant hover:text-primary"
            aria-label="Search"
          >
            <Search className="size-5" />
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="text-on-surface-variant hover:text-primary"
            aria-label="Share"
          >
            <Share2 className="size-5" />
          </Button>
          {onOpenPdf && (
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className="text-on-surface-variant hover:text-primary lg:hidden"
              aria-label="Open PDF viewer"
              onClick={onOpenPdf}
            >
              <FileType className="size-5" />
            </Button>
          )}
        </div>
      </header>

      <ScrollArea className="flex-1 chat-scrollbar">
        <div className="space-y-6 p-6">
          <div className="ml-auto flex max-w-[85%] flex-col items-end gap-2">
            <div className="rounded-2xl rounded-tr-none border border-outline-variant/20 bg-surface-container-highest p-4 text-on-surface">
              <p className="text-body-md">
                Can you summarize the key findings regarding neural network
                efficiency in the Research_Paper_v1.pdf?
              </p>
            </div>
            <span className="text-label-md text-on-surface-variant">
              10:24 AM
            </span>
          </div>

          <div className="flex max-w-[90%] flex-col items-start gap-2">
            <div className="mb-1 flex items-center gap-2">
              <div className="flex size-6 items-center justify-center rounded-md bg-primary/20">
                <Sparkles className="size-4 fill-primary text-primary" />
              </div>
              <span className="text-label-md font-bold text-primary">
                AI ANALYST
              </span>
            </div>
            <div className="glass-effect rounded-2xl rounded-tl-none border-l-4 border-primary p-5 text-on-surface shadow-lg">
              <p className="mb-4 text-body-md leading-relaxed">
                The paper identifies three primary factors driving neural network
                efficiency:
              </p>
              <ul className="space-y-3">
                <li className="flex gap-3">
                  <span className="font-bold text-primary">•</span>
                  <span>
                    <strong className="text-on-surface">Parameter Pruning:</strong>{" "}
                    Reducing the number of non-essential connections by 40%
                    without losing accuracy. <CitationChip page={12} />
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-primary">•</span>
                  <span>
                    <strong className="text-on-surface">Quantization:</strong> Moving
                    from 32-bit to 8-bit precision significantly lowers power
                    consumption while maintaining a 98.4% inference reliability.{" "}
                    <CitationChip page={14} />
                  </span>
                </li>
              </ul>
              <div className="mt-4 border-t border-outline-variant/10 pt-4">
                <p className="text-body-sm text-on-surface-variant italic">
                  Source: Research_Paper_v1.pdf • Verified by DocuChat Engine
                </p>
              </div>
            </div>
            <div className="mt-1 flex gap-2">
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="text-on-surface-variant hover:text-primary"
                aria-label="Thumbs up"
              >
                <ThumbsUp className="size-[18px]" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="text-on-surface-variant hover:text-primary"
                aria-label="Copy"
              >
                <Copy className="size-[18px]" />
              </Button>
            </div>
          </div>

          <div className="ml-auto flex max-w-[85%] flex-col items-end gap-2">
            <div className="rounded-2xl rounded-tr-none border border-outline-variant/20 bg-surface-container-highest p-4 text-on-surface">
              <p className="text-body-md">
                What does the graph on page 15 indicate about latency?
              </p>
            </div>
          </div>

          <div className="flex animate-pulse items-center gap-3 text-primary">
            <Loader2 className="size-5 animate-spin" aria-hidden />
            <span className="text-label-md">
              Analyzing Figure 4.2 in Research_Paper_v1.pdf...
            </span>
          </div>
        </div>
      </ScrollArea>

      <div className="p-6 pt-2">
        <div className="relative mx-auto max-w-4xl">
          <div className="glass-effect flex items-end gap-2 rounded-2xl border border-outline-variant/30 p-2 shadow-2xl">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="shrink-0 rounded-xl text-on-surface-variant hover:bg-surface-container-highest hover:text-primary"
              aria-label="Attach file"
            >
              <Paperclip className="size-5" />
            </Button>
            <Textarea
              ref={textareaRef}
              rows={1}
              placeholder="Ask about your documents..."
              onInput={resizeTextarea}
              className="max-h-48 min-h-0 flex-1 resize-none border-0 bg-transparent px-2 py-3 shadow-none focus-visible:ring-0"
            />
            <Button
              type="button"
              size="icon"
              className="shrink-0 rounded-xl bg-primary text-on-primary shadow-lg shadow-primary/20 hover:opacity-90"
              aria-label="Send message"
            >
              <Send className="size-5" />
            </Button>
          </div>
          <div className="mt-3 flex flex-wrap gap-4 px-2">
            {QUICK_ACTIONS.map(({ icon: Icon, label }) => (
              <button
                key={label}
                type="button"
                className="flex items-center gap-1 text-[11px] font-semibold tracking-wide text-on-surface-variant uppercase transition-all hover:text-primary"
              >
                <Icon className="size-3.5" aria-hidden />
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function PdfViewerPanel() {
  return (
    <div className="flex h-full flex-col bg-surface-container-low">
      <header className="flex items-center justify-between border-b border-outline-variant/10 bg-surface-container-low/50 px-5 py-4 backdrop-blur-sm">
        <div className="flex min-w-0 items-center gap-3">
          <FileType className="size-5 shrink-0 text-secondary" aria-hidden />
          <div className="flex min-w-0 flex-col">
            <h3 className="truncate text-body-sm font-semibold">
              Research_Paper_v1.pdf
            </h3>
            <span className="text-[10px] text-on-surface-variant">
              Page 14 of 42
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="rounded-md hover:bg-surface-container-high"
            aria-label="Zoom out"
          >
            <ZoomOut className="size-5" />
          </Button>
          <span className="px-2 text-label-md">85%</span>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="rounded-md hover:bg-surface-container-high"
            aria-label="Zoom in"
          >
            <ZoomIn className="size-5" />
          </Button>
          <Separator
            orientation="vertical"
            className="mx-2 h-4 bg-outline-variant/30"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="rounded-md hover:bg-surface-container-high"
            aria-label="Fullscreen"
          >
            <Maximize className="size-5" />
          </Button>
        </div>
      </header>

      <ScrollArea className="relative flex-1 chat-scrollbar">
        <div className="relative bg-surface-container-lowest/50 p-8">
          <div className="relative mx-auto aspect-[1/1.41] max-w-md overflow-hidden bg-white p-12 shadow-2xl">
            <div className="mb-6 h-4 w-3/4 bg-slate-200" />
            <div className="mb-3 h-3 w-full bg-slate-100" />
            <div className="mb-3 h-3 w-full bg-slate-100" />
            <div className="mb-8 h-3 w-5/6 bg-slate-100" />
            <div className="relative">
              <div className="absolute -inset-1 animate-pulse border-l-2 border-primary bg-primary/20" />
              <div className="mb-3 h-3 w-full bg-slate-200" />
              <div className="mb-3 h-3 w-full bg-slate-200" />
            </div>
            <div className="mb-12 h-3 w-4/5 bg-slate-100" />
            <div className="flex aspect-video w-full flex-col items-center justify-center rounded border border-dashed border-slate-300 bg-slate-50 p-4">
              <div className="flex h-full w-full items-end gap-2">
                <div className="h-[40%] w-4 rounded-t-sm bg-primary/40" />
                <div className="h-[65%] w-4 rounded-t-sm bg-primary/40" />
                <div className="h-[85%] w-4 rounded-t-sm bg-primary" />
                <div className="h-[55%] w-4 rounded-t-sm bg-primary/40" />
                <div className="h-[70%] w-4 rounded-t-sm bg-primary/40" />
              </div>
              <span className="mt-2 text-[8px] text-slate-400">
                Figure 4.2: Inference Latency Comparison
              </span>
            </div>
            <div className="mt-8 h-3 w-full bg-slate-100" />
            <div className="mt-3 h-3 w-2/3 bg-slate-100" />
            <div className="absolute right-8 bottom-8 text-[10px] text-slate-300 select-none">
              CONFIDENTIAL RESEARCH
            </div>
          </div>

          <div className="glass-effect absolute top-1/2 left-4 flex -translate-y-1/2 flex-col gap-2 rounded-full border border-outline-variant/30 p-2">
            {[Pencil, StickyNote, Highlighter].map((Icon, i) => (
              <Button
                key={i}
                type="button"
                variant="ghost"
                size="icon-sm"
                className="rounded-full text-on-surface-variant hover:bg-primary/20 hover:text-primary"
                aria-label={["Edit", "Note", "Highlight"][i]}
              >
                <Icon className="size-5" />
              </Button>
            ))}
          </div>
        </div>
      </ScrollArea>

      <footer className="border-t border-outline-variant/10 bg-surface-container-low p-4">
        <div className="flex items-center justify-center gap-4">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="gap-1 text-label-md text-on-surface-variant hover:text-primary"
          >
            <ChevronLeft className="size-4" />
            Previous
          </Button>
          <div className="rounded bg-surface-container px-3 py-1 text-label-md font-bold text-on-surface">
            14
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="gap-1 text-label-md text-on-surface-variant hover:text-primary"
          >
            Next
            <ChevronRight className="size-4" />
          </Button>
        </div>
      </footer>
    </div>
  );
}

export function ChatWorkspace() {
  const isLg = useMediaQuery("(min-width: 1024px)");
  const navRef = usePanelRef();
  const pdfRef = usePanelRef();
  const [navCollapsed, setNavCollapsed] = useState(false);
  const [pdfCollapsed, setPdfCollapsed] = useState(false);
  const [mobilePdfOpen, setMobilePdfOpen] = useState(false);
  const [selectedDocId, setSelectedDocId] = useState<string>(DOCUMENTS[0].id);

  const toggleNav = useCallback(() => {
    const panel = navRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) {
      panel.expand();
      setNavCollapsed(false);
    } else {
      panel.collapse();
      setNavCollapsed(true);
    }
  }, []);

  const togglePdf = useCallback(() => {
    const panel = pdfRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) {
      panel.expand();
      setPdfCollapsed(false);
    } else {
      panel.collapse();
      setPdfCollapsed(true);
    }
  }, []);

  const openPdfOnMobile = useCallback(() => {
    if (!isLg) setMobilePdfOpen(true);
  }, [isLg]);

  return (
    <>
    <ResizablePanelGroup
      orientation="horizontal"
      className="h-full min-h-0"
      id="docuchat-chat-layout"
    >
      <ResizablePanel
        panelRef={navRef}
        id="nav"
        defaultSize={18}
        minSize={isLg ? 4 : 0}
        maxSize={28}
        collapsible
        collapsedSize={4}
        className="relative min-w-0"
      >
        <NavSidebar
          collapsed={navCollapsed}
          selectedDocId={selectedDocId}
          onSelectDoc={setSelectedDocId}
        />
        <SidebarToggle
          side="left"
          collapsed={navCollapsed}
          onToggle={toggleNav}
        />
      </ResizablePanel>

      <ResizableHandle withHandle className="bg-outline-variant/20" />

      <ResizablePanel
        id="chat"
        defaultSize={isLg ? 46 : 80}
        minSize={35}
        className="min-w-0"
      >
        <ChatPanel onOpenPdf={!isLg ? openPdfOnMobile : undefined} />
      </ResizablePanel>

      {isLg && (
        <>
          <ResizableHandle withHandle className="bg-outline-variant/20" />
          <ResizablePanel
            panelRef={pdfRef}
            id="pdf"
            defaultSize={36}
            minSize={22}
            maxSize={55}
            collapsible
            collapsedSize={0}
            className="relative min-w-0"
          >
            <PdfViewerPanel />
            <SidebarToggle
              side="right"
              collapsed={pdfCollapsed}
              onToggle={togglePdf}
            />
          </ResizablePanel>
        </>
      )}
    </ResizablePanelGroup>

    {!isLg && mobilePdfOpen && (
      <div className="fixed inset-0 z-50 flex flex-col bg-surface-container-low">
        <div className="flex justify-end border-b border-outline-variant/10 p-2">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={() => setMobilePdfOpen(false)}
            aria-label="Close PDF viewer"
          >
            <X className="size-5" />
          </Button>
        </div>
        <div className="min-h-0 flex-1">
          <PdfViewerPanel />
        </div>
      </div>
    )}
    </>
  );
}
