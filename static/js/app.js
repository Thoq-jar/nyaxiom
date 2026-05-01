const UPDATE_INTERVAL = document.body.dataset.updateInterval * 1000 || 5000;

const isOnPage = (page) => {
  const address = window.location.origin;
  const currentUrl = window.location.href;
  const targetUrl = `${address}/${page}`;
  return currentUrl === targetUrl || currentUrl === `${targetUrl}/`;
};

async function updateStats() {
  if (isOnPage("") || isOnPage("index.html")) {
    try {
      const [cpuResponse, ramResponse] = await Promise.all([
        fetch("/api/hardware/cpu/usage"),
        fetch("/api/hardware/ram/usage"),
      ]);

      const cpuData = await cpuResponse.json();
      const ramData = await ramResponse.json();

      updateDial("CPU", cpuData.usage);
      updateDial("RAM", ramData.usage);
    } catch (error) {
      console.error("Error updating statistics:", error);
    }
  } else if (isOnPage("cpu")) {
    try {
      const response = await fetch("/api/hardware/cpu/core_usage");
      const data = await response.json();

      data.forEach((coreDict) => {
        for (const [id, usage] of Object.entries(coreDict)) {
          updateDial(`Core ${id}`, usage);
        }
      });
    } catch (error) {
      console.error("Error updating CPU statistics:", error);
    }
  } else if (isOnPage("memory")) {
    try {
      const response = await fetch("/api/hardware/ram/free_used");
      const data = await response.json();

      updateDial("Used", data.used);
      updateDial("Free", data.free);
    } catch (error) {
      console.error("Error updating memory statistics:", error);
    }
  }
}

function updateDial(title, percentage) {
  const cards = document.querySelectorAll(".stat-card");
  cards.forEach((card) => {
    if (card.querySelector(".stat-title").textContent === title) {
      const circle = card.querySelector(".progress-value");
      const dot = card.querySelector(".progress-dot");
      const text = card.querySelector(".progress-text");

      const circumference = 282.74;
      const offset = circumference - (circumference * percentage) / 100;

      circle.style.strokeDashoffset = offset;
      dot.style.transform = `rotate(${percentage * 3.6}deg) translate(45px)`;
      text.textContent = Math.round(percentage) + "%";
    }
  });
}

let logData = [];
let selectedLogs = new Set();
let isFetchingLogs = false;
let filteredLogLines = [];
let currentRenderStartIndex = -1;
let currentRenderEndIndex = -1;
const VISIBLE_ROW_BUFFER = 20;

async function updateLogs() {
  if (!isOnPage("logs") || isFetchingLogs) {
    return;
  }

  const liveUpdateCheckbox = document.getElementById("live-update");
  const liveUpdate = liveUpdateCheckbox ? liveUpdateCheckbox.checked : false;

  if (!liveUpdate && logData.length > 0) {
    return;
  }

  isFetchingLogs = true;
  const statusElement = document.getElementById("log-status");
  if (statusElement) {
    statusElement.textContent = "Updating...";
  }

  try {
    const response = await fetch("/api/os/logs/retrieve");
    const data = await response.json();
    logData = data;

    renderLogList();
    prepareLogContent();

    if (statusElement) {
      const now = new Date();
      statusElement.textContent = `Last updated: ${now.toLocaleTimeString()}`;
    }
  } catch (error) {
    console.error("Error updating logs:", error);
    if (statusElement) {
      statusElement.textContent = "Update failed";
    }
  } finally {
    isFetchingLogs = false;
  }
}

function renderLogList() {
  const listElement = document.getElementById("log-list");
  if (!listElement) {
    return;
  }

  const currentListHtml = logData
    .map((log) => {
      return /* HTML */ `
        <div class="log-item" onclick="toggleLogSelection('${log.id}')">
          <input
            type="checkbox"
            id="checkbox-${log.id}"
            ${selectedLogs.has(log.id) ? "checked" : ""}
            onchange="event.stopPropagation(); toggleLogSelection('${log.id}')"
          />
          <span title="${log.id}">${log.name}</span>
        </div>
      `;
    })
    .join("");

  if (listElement.innerHTML !== currentListHtml && currentListHtml !== "") {
    listElement.innerHTML = currentListHtml;
  } else if (currentListHtml === "") {
    listElement.innerHTML = /* HTML */ `<div class="loading-spinner">
      No logs found
    </div>`;
  }
}

function toggleLogSelection(identifier) {
  if (selectedLogs.has(identifier)) {
    selectedLogs.delete(identifier);
  } else {
    selectedLogs.add(identifier);
  }
  renderLogList();
  prepareLogContent();
}

function prepareLogContent() {
  const containerElement = document.getElementById("log-container");
  if (!containerElement) {
    return;
  }

  if (selectedLogs.size === 0) {
    filteredLogLines = [];
    containerElement.innerHTML = /* HTML */ `<div class="log-placeholder">
      Select a log file to view content...
    </div>`;
    return;
  }

  const searchInputElement = document.getElementById("log-search");
  const searchTerm = searchInputElement ? searchInputElement.value : "";

  const useRegexCheckbox = document.getElementById("use-regex");
  const useRegex = useRegexCheckbox ? useRegexCheckbox.checked : false;

  const autoScrollCheckbox = document.getElementById("auto-scroll");
  const autoScroll = autoScrollCheckbox ? autoScrollCheckbox.checked : false;

  const containerWidth =
    containerElement.clientWidth > 0 ? containerElement.clientWidth - 40 : 800;
  const charWidth = 7.8;
  const charsPerLine = Math.max(40, Math.floor(containerWidth / charWidth));

  filteredLogLines = [];
  let currentOffsetY = 0;

  logData.forEach((log) => {
    if (selectedLogs.has(log.id)) {
      const lines = log.content.split("\n");
      lines.forEach((line) => {
        if (!line.trim()) {
          return;
        }

        let isMatch = true;
        if (searchTerm !== "") {
          if (useRegex) {
            try {
              const regularExpression = new RegExp(searchTerm, "i");
              isMatch = regularExpression.test(line);
            } catch (error) {
              isMatch = true;
            }
          } else {
            isMatch = line.toLowerCase().includes(searchTerm.toLowerCase());
          }
        }

        if (isMatch) {
          const prefixLength = log.name.length + 3;
          const textLength = line.length + prefixLength;
          const wrappedLines = Math.ceil(textLength / charsPerLine) || 1;
          const height = wrappedLines * 21 + 4;

          filteredLogLines.push({
            logName: log.name,
            line: line,
            isMatch: searchTerm !== "",
            offset: currentOffsetY,
            height: height,
          });

          currentOffsetY += height;
        }
      });
    }
  });

  currentRenderStartIndex = -1;
  renderVirtualScroll(true);

  if (autoScroll) {
    setTimeout(() => {
      containerElement.scrollTop = containerElement.scrollHeight;
    }, 0);
  }
}

function renderVirtualScroll(forceUpdate = false) {
  const containerElement = document.getElementById("log-container");
  if (!containerElement) {
    return;
  }

  if (filteredLogLines.length === 0 && selectedLogs.size > 0) {
    containerElement.innerHTML = /* HTML */ `<div class="log-placeholder">
      No matching log lines found
    </div>`;
    return;
  }

  if (filteredLogLines.length === 0) {
    return;
  }

  const scrollTop = containerElement.scrollTop;
  const containerHeight = containerElement.clientHeight || 500;

  let startIndex = 0;
  let low = 0;
  let high = filteredLogLines.length - 1;

  while (low <= high) {
    const MathMid = Math.floor((low + high) / 2);
    if (filteredLogLines[MathMid].offset === scrollTop) {
      startIndex = MathMid;
      break;
    } else if (filteredLogLines[MathMid].offset < scrollTop) {
      startIndex = MathMid;
      low = MathMid + 1;
    } else {
      high = MathMid - 1;
    }
  }

  startIndex = Math.max(0, startIndex - VISIBLE_ROW_BUFFER);

  let endIndex = startIndex;
  while (
    endIndex < filteredLogLines.length &&
    filteredLogLines[endIndex].offset < scrollTop + containerHeight
  ) {
    endIndex++;
  }
  endIndex = Math.min(filteredLogLines.length, endIndex + VISIBLE_ROW_BUFFER);

  if (
    !forceUpdate &&
    Math.abs(startIndex - currentRenderStartIndex) < 5 &&
    Math.abs(endIndex - currentRenderEndIndex) < 5
  ) {
    return;
  }

  currentRenderStartIndex = startIndex;
  currentRenderEndIndex = endIndex;

  const totalHeight =
    filteredLogLines.length > 0
      ? filteredLogLines[filteredLogLines.length - 1].offset +
        filteredLogLines[filteredLogLines.length - 1].height
      : 0;
  const offsetY =
    filteredLogLines.length > 0 ? filteredLogLines[startIndex].offset : 0;

  const visibleLines = filteredLogLines.slice(startIndex, endIndex);

  const linesHtml = visibleLines
    .map((item) => {
      return /* HTML */ `
        <div class="log-line ${item.isMatch ? "match" : ""}">
          <span
            style="color: var(--accent); opacity: 0.7; font-size: 0.8em; margin-right: 8px;"
            >[${item.logName}]</span
          >${escapeHtml(item.line)}
        </div>
      `;
    })
    .join("");

  containerElement.innerHTML = /* HTML */ `
    <div style="height: ${totalHeight}px; position: relative; width: 100%;">
      <div style="position: absolute; top: ${offsetY}px; left: 0; right: 0;">
        ${linesHtml}
      </div>
    </div>
  `;
}

function escapeHtml(text) {
  const divElement = document.createElement("div");
  divElement.textContent = text;
  return divElement.innerHTML;
}

function initTheme() {
  const savedTheme = localStorage.getItem("axiom-theme");
  if (savedTheme === "light") {
    document.documentElement.classList.add("light");
  }
  const themeToggleElement = document.getElementById("theme-toggle");
  if (themeToggleElement) {
    themeToggleElement.addEventListener("click", () => {
      const toggleTheme = () => {
        document.documentElement.classList.toggle("light");
        const isLight = document.documentElement.classList.contains("light");
        localStorage.setItem("axiom-theme", isLight ? "light" : "dark");

        const imgIcon = themeToggleElement.querySelector(".theme-icon");
        if (imgIcon) {
          imgIcon.src = isLight
            ? "/static/image/icons/moon.svg"
            : "/static/image/icons/light.svg";
        }
      };

      if (!document.startViewTransition) {
        toggleTheme();
        return;
      }

      document.startViewTransition(() => {
        toggleTheme();
      });
    });

    const imgIcon = themeToggleElement.querySelector(".theme-icon");
    if (imgIcon) {
      imgIcon.src =
        savedTheme === "light"
          ? "/static/image/icons/moon.svg"
          : "/static/image/icons/light.svg";
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();

  const logSearchElement = document.getElementById("log-search");

  if (logSearchElement) {
    logSearchElement.addEventListener("input", prepareLogContent);
  }

  const useRegexElement = document.getElementById("use-regex");
  if (useRegexElement) {
    useRegexElement.addEventListener("change", prepareLogContent);
  }

  const autoScrollElement = document.getElementById("auto-scroll");
  if (autoScrollElement) {
    autoScrollElement.addEventListener("change", prepareLogContent);
  }

  const refreshLogListElement = document.getElementById("refresh-log-list");
  if (refreshLogListElement) {
    refreshLogListElement.addEventListener("click", updateLogs);
  }

  const clearLogsElement = document.getElementById("clear-logs");
  if (clearLogsElement) {
    clearLogsElement.addEventListener("click", () => {
      selectedLogs.clear();
      renderLogList();
      prepareLogContent();
    });
  }

  const logContainerElement = document.getElementById("log-container");
  if (logContainerElement) {
    logContainerElement.addEventListener("scroll", () => {
      renderVirtualScroll();
    });

    window.addEventListener("resize", () => {
      if (selectedLogs.size > 0) {
        prepareLogContent();
      }
    });
  }
});

setInterval(updateStats, UPDATE_INTERVAL);
setInterval(updateLogs, UPDATE_INTERVAL);
updateStats();
updateLogs();
