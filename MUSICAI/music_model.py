import torch
import torch.nn as nn

class MusicGenerationModel(nn.Module):
    def __init__(self, 
                 input_size: int = 256,
                 hidden_size: int = 512,
                 num_layers: int = 4,
                 dropout: float = 0.1):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )
        
        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=8,
            dim_feedforward=2048,
            dropout=dropout
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose1d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose1d(32, 1, kernel_size=4, stride=2, padding=1),
            nn.Tanh()
        )
        
        # Style embedding
        self.style_embedding = nn.Embedding(num_embeddings=5, embedding_dim=hidden_size)
        
    def forward(self, x, style_idx):
        # Input shape: [batch_size, 1, sequence_length]
        
        # Encode
        x = self.encoder(x)  # [batch_size, 128, sequence_length/8]
        
        # Reshape for transformer
        x = x.permute(2, 0, 1)  # [sequence_length/8, batch_size, 128]
        
        # Get style embedding
        style = self.style_embedding(style_idx)  # [batch_size, hidden_size]
        style = style.unsqueeze(0).repeat(x.size(0), 1, 1)  # [sequence_length/8, batch_size, hidden_size]
        
        # Combine features with style
        x = torch.cat([x, style], dim=-1)  # [sequence_length/8, batch_size, 128 + hidden_size]
        
        # Transform
        x = self.transformer(x)  # [sequence_length/8, batch_size, hidden_size]
        
        # Reshape for decoder
        x = x.permute(1, 2, 0)  # [batch_size, hidden_size, sequence_length/8]
        
        # Decode
        x = self.decoder(x)  # [batch_size, 1, sequence_length]
        
        return x
    
    def generate(self, input_sequence, style_idx, max_length=65536):
        """Generate a new sequence in the specified style"""
        self.eval()
        with torch.no_grad():
            # Process input
            x = input_sequence.unsqueeze(0)  # Add batch dimension
            output = self.forward(x, style_idx)
            
            # Remove batch dimension
            output = output.squeeze(0)
            
            return output
