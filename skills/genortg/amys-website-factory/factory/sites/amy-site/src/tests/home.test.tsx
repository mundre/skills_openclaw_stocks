import { render, screen } from '@testing-library/react';
import React from 'react';
import { vi } from 'vitest';

// Mock ThreeHero to avoid WebGL in tests
vi.mock('../components/ThreeHero', () => ({
  default: () => <div data-testid="three-hero">ThreeHeroMock</div>,
}));

// Mock framer-motion's motion to a plain div
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

import HomePage from '../app/page';

test('Home page renders hero and features', () => {
  render(<HomePage />);
  expect(screen.getByText(/Meet AMY/i)).toBeTruthy();
  expect(screen.getByTestId('three-hero')).toBeTruthy();
});
