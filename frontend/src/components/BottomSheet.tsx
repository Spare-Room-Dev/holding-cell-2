'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { ReactNode } from 'react';

/**
 * BottomSheet component for mobile stats display.
 * Per CONTEXT.md D-05 through D-08:
 * - Slide-up animation with backdrop
 * - Tap outside or swipe down dismisses
 * - Max height 70vh to prevent full screen coverage
 */
interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
}

export function BottomSheet({ isOpen, onClose, children }: BottomSheetProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop - semi-transparent overlay that dismisses on tap */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Sheet - slides up from bottom with spring animation */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.2}
            onDragEnd={(_, { offset, velocity }) => {
              // Close if dragged down significantly or with velocity
              if (offset.y > 100 || velocity.y > 500) {
                onClose();
              }
            }}
            className="fixed bottom-0 left-0 right-0 bg-surface-raised rounded-t-lg border-t border-border z-50 max-h-[70vh] overflow-y-auto p-lg"
            role="dialog"
            aria-modal="true"
          >
            {/* Drag handle - visual indicator at top */}
            <div className="w-12 h-1 bg-text-subtle rounded-full mx-auto mb-md" />
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}