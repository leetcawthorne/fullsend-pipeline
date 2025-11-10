source "https://rubygems.org"

ruby ">= 3.3.0"

# Core
gem "jekyll", "~> 4.3.3"

# Required for Ruby 3.3+ (no longer in stdlib)
gem "csv"
gem "logger"

# Common plugins
group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
  gem "jekyll-seo-tag", "~> 2.8"
  gem "jekyll-sitemap", "~> 1.4"
end

# Optional: only enable this for GitHub Pages builds
group :github_pages do
  gem "github-pages", "~> 231", require: false
end
