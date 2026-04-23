import { render, screen } from '@testing-library/react';
import React from 'react';
import { vi } from 'vitest';

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, className }: any) => (
    <a href={href} className={className}>{children}</a>
  ),
}));

import { SiteFooter } from '../components/SiteFooter';

test('renders SiteFooter with links and aria label', () => {
  render(<SiteFooter />);
  expect(screen.getByText(/LLM skill showcase/i)).toBeTruthy();
  expect(screen.getByText(/Home/)).toBeTruthy();
  expect(screen.getByLabelText('Site footer')).toBeTruthy();
});
