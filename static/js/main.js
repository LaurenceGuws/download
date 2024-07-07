import { initializeFetchForm } from './fetch.js';
import { initializeDownloadButton } from './download.js';
import { initializeProgressEventSource } from './progress.js';

document.addEventListener('DOMContentLoaded', () => {
    initializeFetchForm();
    initializeDownloadButton();
    initializeProgressEventSource();
});
