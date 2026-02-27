// IdeaShelf - Content Script
// Extracts selected text and surrounding context on request from background.js.
// Minimal footprint: no DOM modification, no persistent listeners beyond message handler.

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "get-selection") {
    const selection = window.getSelection();
    const selectedText = selection ? selection.toString().trim() : "";

    let precedingText = "";
    let followingText = "";

    if (selection && selection.rangeCount > 0 && selectedText) {
      try {
        const range = selection.getRangeAt(0);

        // Get the text content of the container for context extraction
        const container = range.commonAncestorContainer;
        const fullText =
          container.nodeType === Node.TEXT_NODE
            ? container.textContent
            : container.textContent || "";

        if (fullText && container.nodeType === Node.TEXT_NODE) {
          const startOffset = range.startOffset;
          const endOffset = range.endOffset;

          precedingText = fullText
            .substring(Math.max(0, startOffset - 50), startOffset)
            .trim();
          followingText = fullText
            .substring(endOffset, endOffset + 50)
            .trim();
        } else if (fullText) {
          // For element nodes, find the selection within the full text
          const selIndex = fullText.indexOf(selectedText);
          if (selIndex >= 0) {
            precedingText = fullText
              .substring(Math.max(0, selIndex - 50), selIndex)
              .trim();
            followingText = fullText
              .substring(
                selIndex + selectedText.length,
                selIndex + selectedText.length + 50
              )
              .trim();
          }
        }
      } catch (e) {
        // Context extraction failed silently; selectedText still returned
      }
    }

    sendResponse({
      selectedText: selectedText,
      precedingText: precedingText,
      followingText: followingText,
      pageUrl: window.location.href,
      pageTitle: document.title,
    });
  }
});
